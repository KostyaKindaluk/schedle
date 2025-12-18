from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Scheduling
from .serializers import (
	SchedulingCreateSerializer,
	SchedulingListSerializer,
	SchedulingDetailSerializer
)
from algorithm.manager import get_manager


class SchedulingViewSet(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]
	
	def get_queryset(self):
		return Scheduling.objects.filter(user=self.request.user)
	
	def get_serializer_class(self):
		if self.action == 'create':
			return SchedulingCreateSerializer
		elif self.action == 'list':
			return SchedulingListSerializer
		return SchedulingDetailSerializer
	
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		
		scheduling = serializer.save(user=request.user)
		
		self._start_algorithm(scheduling)
		
		return Response(
			SchedulingDetailSerializer(scheduling).data,
			status=status.HTTP_201_CREATED
		)
	
	def _start_algorithm(self, scheduling: Scheduling):
		manager = get_manager()
		
		def make_save_callback(sched_id):
			def save_checkpoint(generation, population, best_fitness):
				try:
					sched = Scheduling.objects.get(id=sched_id)
					sched.save_checkpoint(generation, population, best_fitness)
				except Scheduling.DoesNotExist:
					pass
			return save_checkpoint
		
		def make_update_callback(sched_id):
			def update_status(new_status, result=None):
				try:
					sched = Scheduling.objects.get(id=sched_id)
					if new_status == 'completed' and result:
						sched.save_results(
							schedules=[result['schedule']],
							fitness=result['fitness']
						)
					else:
						sched.status = new_status
						sched.save(update_fields=['status', 'updated_at'])
				except Scheduling.DoesNotExist:
					pass
			return update_status
		
		input_data = scheduling.get_input_data()
		
		checkpoint_data = None
		if scheduling.checkpoint_population:
			checkpoint_data = {
				'generation': scheduling.checkpoint_generation,
				'population': scheduling.checkpoint_population,
				'best_fitness': scheduling.checkpoint_best_fitness
			}
		
		try:
			manager.start_scheduling(
				scheduling_id=scheduling.id,
				input_data=input_data,
				save_callback=make_save_callback(scheduling.id),
				update_status_callback=make_update_callback(scheduling.id),
				checkpoint_data=checkpoint_data
			)
		except ValueError as e:
			return Response(
				{'error': str(e)},
				status=status.HTTP_400_BAD_REQUEST
			)
	
	def retrieve(self, request, pk=None):
		scheduling = self.get_object()
		serializer = self.get_serializer(scheduling)
		data = serializer.data
		
		if scheduling.status == 'in_progress':
			manager = get_manager()
			runtime_status = manager.get_status(scheduling.id)
			if runtime_status:
				data['current_generation'] = runtime_status['generation']
				data['current_best_fitness'] = runtime_status['best_fitness']
		
		return Response(data)
	
	def destroy(self, request, pk=None):
		scheduling = self.get_object()
		
		if scheduling.status == 'in_progress':
			manager = get_manager()
			try:
				manager.cancel_scheduling(scheduling.id)
			except ValueError:
				pass
		
		scheduling.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)