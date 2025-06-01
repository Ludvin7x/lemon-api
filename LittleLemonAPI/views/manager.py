from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from ..permissions import IsManagerOrAdmin, IsAdmin

class ManagerGroupView(APIView):
    group_name = 'Manager'

    def get_permissions(self):
        return [IsAuthenticated(), (IsManagerOrAdmin() | IsAdmin())]

    def get(self, request):
        group = get_object_or_404(Group, name=self.group_name)
        users = [{'id': u.id, 'username': u.username} for u in group.user_set.all()]
        return Response(users)

    def post(self, request):
        group = get_object_or_404(Group, name=self.group_name)
        user = get_object_or_404(User, pk=request.data.get('user_id'))
        group.user_set.add(user)
        return Response({'detail': 'User added to Manager group.'}, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        group = get_object_or_404(Group, name=self.group_name)
        user = get_object_or_404(User, pk=user_id)
        group.user_set.remove(user)
        return Response({'detail': 'User removed from Manager group.'}, status=status.HTTP_200_OK)