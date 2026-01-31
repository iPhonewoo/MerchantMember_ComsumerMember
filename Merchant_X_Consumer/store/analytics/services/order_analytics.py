from datetime import date, timedelta, datetime
from decimal import Decimal
from dataclasses import dataclass

from django.db.models import (
    Count, Sum, F, ExpressionWrapper, DecimalField, Max
)
from django.db.models.functions import Coalesce, TruncDate, TruncMonth

from store.models import Order, OrderItem
from member.models import Merchant


@dataclass(frozen=True)
class OrderSummary:
    start: date | None
    end: date | None
    order_count: int
    gmv: Decimal
    aov: Decimal
    status_breakdown: list[dict]


def build_order_summary(
    *,
    merchant: Merchant,
    start: date | None = None,
    end: date | None = None,
) -> OrderSummary:
    """
    計算某個 Merchant 在指定期間內的訂單總覽
    """

    # 先找出那些訂單是「該商家」，當作後面OrderItem的範圍限制
    order_qs = Order.objects.filter(
        items__product__store__merchant=merchant
    )

    # 時間區間
    if start:
        order_qs = order_qs.filter(created_at__date__gte=start)
    if end:
        order_qs = order_qs.filter(created_at__date__lte=end)

    # 訂單數
    order_qs = order_qs.distinct()
    
    order_count = order_qs.count()

    # 只拿屬於該商家的商品，而且是出現在這些訂單裡的
    item_qs = OrderItem.objects.filter(
        product__store__merchant=merchant,
        order__in=order_qs, # 限制在剛剛那些訂單內
    )
    
    # GMV
    gmv = item_qs.aggregate(
        total=Coalesce(
            Sum(F("price_at_purchase") * F("quantity")),
            Decimal("0.00")
        )
    )["total"]

    # AOV
    aov = gmv / order_count if order_count > 0 else Decimal("0.00")

    # 訂單狀態分佈
    status_breakdown = list(
        order_qs.values("status")
                .annotate(count=Count("id", distinct=True)) # 避免 Order JOIN OrderItem 後被放大(重複計算)
                .order_by("status")
    )

    return OrderSummary(
        start=start,
        end=end,
        order_count=order_count,
        gmv=gmv,
        aov=aov,
        status_breakdown=status_breakdown,
    )


def build_order_timeseries(
        *,
        merchant,
        start: date,
        end: date,
        group_by: str = "day",
        statuses: list[str] | None = None,
):
    """
    商家訂單時序分析（可選 status 篩選）
    - 訂單數：distinct Order（符合 status、且包含該商家商品）
    - GMV：只加總該商家商品的銷售額（OrderItem）
    """

    # 先取得該商家的訂單資料
    order_qs = Order.objects.filter(
        items__product__store__merchant=merchant,
        created_at__date__gte=start,
        created_at__date__lte=end,
    ).distinct()

    if statuses:
        order_qs = order_qs.filter(status__in=statuses)
    
    order_qs = order_qs.distinct()

    # 設定時間分組的方式
    if group_by == "month":
        trunc = TruncMonth("order__created_at")
    else:
        trunc = TruncDate("order__created_at")

    # 用 OrderItem 算 GMV
    item_qs = OrderItem.objects.filter(
        product__store__merchant=merchant,
        order__in=order_qs,
    )

    aggregated = (
        item_qs
        .annotate(period=trunc)
        .values("period")
        .annotate(
            gmv=Coalesce(
                Sum(F("price_at_purchase") * F("quantity")),
                Decimal("0.00")
            ),
            order_count=Count("order", distinct=True),
        ).order_by("period")
    )

    # 將所有日期資料轉乘dict, 且都為date物件
    data_map = {
        row["period"].date() if isinstance(row["period"], datetime) else row["period"]: 
        row for row in aggregated
    }

    series = []
    current = start

    # 補齊沒有訂單的日期
    while current <= end:
        key = current if group_by == "day" else current.replace(day=1)
        row = data_map.get(key)

        series.append({
            "date": key,
            "order_count": row["order_count"] if row else 0,
            "gmv": row["gmv"] if row else Decimal("0.00"),
        })

        current += timedelta(days=1 if group_by == "day" else 32)
        if group_by == "month":
            current = current.replace(day=1)

    return series


def build_top_products(
    *,
    merchant,
    start: date,
    end: date,
    limit: int = 10,
    statuses: list[str] | None = None,    
):
    """
    熱門商品分析
    """

    if statuses is None:
        statuses = [Order.StatusChoices.PAID, Order.StatusChoices.COMPLETED]

    qs = OrderItem.objects.filter(
        product__store__merchant=merchant,
        order__created_at__date__gte=start,
        order__created_at__date__lte=end,
        order__status__in=statuses,
    )

    qs = qs.annotate(
        revenue_item=ExpressionWrapper(
            F("price_at_purchase") * F("quantity"),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    )
    
    aggregated = (
        qs.values(
            "product_id",
            "product__name",
        )
        .annotate(
            quantity=Coalesce(Sum("quantity"), 0),
            revenue=Coalesce(Sum("revenue_item"), Decimal("0.00")),
            order_count=Count("order", distinct=True),
        ).order_by("-quantity")[:limit]
    )

    return list(aggregated)


def build_top_customers(
        *,
        merchant,
        start: date,
        end: date,
        limit: int = 5,
        statuses: list[str] | None = None,
):
    """
    熟客分析
    """
    
    if statuses is None:
        statuses = [Order.StatusChoices.PAID, Order.StatusChoices.COMPLETED]

    qs = OrderItem.objects.filter(
        product__store__merchant=merchant,
        order__created_at__date__gte=start,
        order__created_at__date__lte=end,
        order__status__in=statuses,
    )
    
    qs = qs.annotate(
        item_gmv=ExpressionWrapper(
            F("price_at_purchase") * F("quantity"),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    )

    aggregated = (
        qs.values(
            "order__member_id",
            "order__member__user__username",
        )
        .annotate(
            total_gmv=Coalesce(Sum("item_gmv"), Decimal("0.00")),
            order_count=Count("order_id", distinct=True),
            last_order_date=TruncDate(Max("order__created_at")),
        ).order_by("-total_gmv")[:limit]
    )

    return list(aggregated)



