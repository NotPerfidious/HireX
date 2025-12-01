from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import JobPost,Skill
from .serializers import JobSerializer,SkillSerializer


class Jobs(APIView):
    def post(self, request):
        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():
            job_instance = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, id=None):
        if id:
            try:
                job = JobPost.objects.get(id=id)
            except JobPost.DoesNotExist:
                return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = JobSerializer(job)
            return Response(serializer.data)
        jobs = JobPost.objects.all()
        serialized = JobSerializer(jobs, many=True)
        return Response(serialized.data)


    def put(self, request, id):
        try:
            job = JobPost.objects.get(id=id)
        except JobPost.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = JobSerializer(job, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            job = JobPost.objects.get(id=id)
        except JobPost.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        job.delete()
        return Response(
            {"message": "Job deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
    
class AddSkill(APIView):
    def post(self,request):
        serializer=SkillSerializer(data=request.data)
        if serializer.is_valid():
            skill = serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    def get(self,request):
        skills=Skill.objects.all()
        serialized=SkillSerializer(skills,many=True)
        return Response(serialized.data)