from datetime import date
from decimal import Decimal
from dataclasses import dataclass

from django.db.models import Count, Sum, F
from django.db.models.functions import Coalesce

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
