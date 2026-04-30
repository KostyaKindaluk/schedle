from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
	serializer = RegisterSerializer(data=request.data)
	if serializer.is_valid():
		user = serializer.save()
		token = Token.objects.create(user=user)
		
		return Response({
			'user': UserSerializer(user).data,
			'token': token.key
		}, status=status.HTTP_201_CREATED)
	
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
	serializer = LoginSerializer(data=request.data)
	if not serializer.is_valid():
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
	email = serializer.validated_data['email']
	password = serializer.validated_data['password']
	
	user = authenticate(username=email, password=password)
	
	if user is None:
		return Response({
			'error': 'Invalid credentials'
		}, status=status.HTTP_401_UNAUTHORIZED)
	
	token, created = Token.objects.get_or_create(user=user)
	
	return Response({
		'user': UserSerializer(user).data,
		'token': token.key
	})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
	request.user.auth_token.delete()
	
	return Response({'message': 'Successfully logged out'})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
	user = request.user
	user.delete()
	
	return Response({
		'message': 'Account successfully deleted'
	}, status=status.HTTP_204_NO_CONTENT)