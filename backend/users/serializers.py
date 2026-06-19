from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.models import Subscription, User


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        if request is None or request.user.is_anonimus:
            return False

        return Subscription.objects.filter(
            user=request.user,
            author=obj,
        ).exists()


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        from recipes.serializers import RecipeMinifiedSerializer
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeMinifiedSerializer(
            recipes,
            many=True,
            context=self.context,
        ).data


class SetAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class SubscriptionSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )

    class Meta:
        model = Subscription
        fields = (
            'user',
            'author',
        )
        read_only_fields = ('user',)

        def validate(self, data):
            user = self.context['request'].user
            author = data['author']
            if user == author:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя'
                )
            if Subscription.objects.filter(user=user, author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого пользователя'
                )
            return data

        def create(self, validated_data):
            return Subscription.objects.create(
                user=self.context['request'].user,
                author=validated_data['author'],
            )
