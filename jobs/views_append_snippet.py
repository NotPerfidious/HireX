
class InterviewerInterviewListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, 'role', None) != 'interviewer':
            return Response({'detail': 'Only Interviewers can view their interviews'}, status=status.HTTP_403_FORBIDDEN)

        try:
            interviewer = request.user.interviewer
        except Interviewer.DoesNotExist:
             return Response({'detail': 'Interviewer profile not found'}, status=status.HTTP_400_BAD_REQUEST)

        interviews = Interview.objects.filter(interviewer=interviewer).order_by('date', 'start_time')
        serializer = InterviewSerializer(interviews, many=True)
        return Response(serializer.data)
