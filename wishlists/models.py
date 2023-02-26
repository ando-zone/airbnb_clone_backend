from django.db import models
from common.models import CommonModel


class Wishlist(CommonModel):

    """Wishlist Model Definition"""
    # TODO@Ando: 아래 궁금한 점 해결되지 않음.
    # 11.23 니꼬의 강의를 들어보면 아래와 같이 이해하면 안되는 것 같음. ModelSerializer가
    # 그냥 자동으로 blank=True null=True가 아니면 필수라고 생각해야 하는데...
    # 왜 user가 방 이름을 지정하지 않아도 등록이 되었던 걸까??? 궁금함.
    # 아 오케이 해결됨... 일단 11.23 강의를 잘 들어볼 것.

    # TODO@Ando: 궁금한 점. (해결)
    # 여기서 rooms나 experiences는 빈 값? 허용 옵션이 없어서 admin panel에서 추가할 경우,
    # 반드시 값을 같이 줘야 함. --> 이거는 db와는 상관 없이 admin_panel에게 주는 약속 혹은 규칙 같은 것이다.
    # DB에는 어차피 PK만 제대로 있으면 됩니다.
    # 따라서 admin panel의 제약 조건과 API의 제약 조건이 일치하는 것 혹은 일치성을 고려하는 것이 꽤 중요하겠네요.
    # 근데 DRF로 유저가 등록할 때는, 꼭 필요하지 않음. 이래도 괜찮은건가?
    # 왜 이게 가능한거지? DRF가 알아서 우회하게끔 한 것인가? read_only = True라서 그렇습니다.

    name = models.CharField(
        max_length=150,
    )
    rooms = models.ManyToManyField(
        "rooms.Room",
        related_name="wishlists",
    )
    experiences = models.ManyToManyField(
        "experiences.Experience",
        related_name="wishlists",
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="wishlists",
    )

    def __str__(self) -> str:
        return self.name