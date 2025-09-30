from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    ChatRequestSerializer, ChatResponseSerializer,
    RecommendRequestSerializer, RecommendResponseSerializer,
    UploadReportSerializer, UploadReportResponseSerializer,
    GetRecommendationRequestSerializer, GetRecommendationResponseSerializer,
)
from .agents import PatientAgent, ClinicalAgent
from .rag_service import RAGIndex

# Initialize shared components
_RAG = RAGIndex(base_dir=".")
_PATIENT = PatientAgent()
_CLINICAL = ClinicalAgent(_RAG)


# PUBLIC_INTERFACE
@api_view(["POST"])
def chat(request):
    """
    summary: Patient chat endpoint
    description: |
      Engage with the PatientAgent for structured chat. Saves de-identified session notes to OneDrive (with local fallback).
      Ocean Professional style is applied to the API documentation.
    tags:
      - Chat
    requestBody:
      required: true
    responses:
      200:
        description: Successful reply
    """
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    reply, safety = _PATIENT.reply(data["session_id"], data["message"])
    response = ChatResponseSerializer({"reply": reply, "session_id": data["session_id"], "safety": safety})
    return Response(response.data, status=status.HTTP_200_OK)


# PUBLIC_INTERFACE
@api_view(["POST"])
def recommend(request):
    """
    summary: Clinical recommendation (RAG)
    description: |
      Use ClinicalAgent with retrieval-augmented generation over medical guideline documents
      to answer clinical questions. Returns synthesized answer and citations.
    tags:
      - Clinical
    """
    serializer = RecommendRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    answer, citations, safety = _CLINICAL.recommend(
        data["session_id"], data["question"], data.get("top_k", 4)
    )
    resp = RecommendResponseSerializer({"answer": answer, "citations": citations, "safety": safety})
    return Response(resp.data, status=status.HTTP_200_OK)


# PUBLIC_INTERFACE
@api_view(["POST"])
def upload_report(request):
    """
    summary: Upload and refine test report
    description: |
      Upload raw test report text and receive an auto-structured summary for clinician review.
    tags:
      - Reports
    """
    serializer = UploadReportSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    refined, safety = _CLINICAL.refine_report(data["session_id"], data["report_text"])
    resp = UploadReportResponseSerializer({"refined_report": refined, "session_id": data["session_id"], "safety": safety})
    return Response(resp.data, status=status.HTTP_200_OK)


# PUBLIC_INTERFACE
@api_view(["POST"])
def get_recommendation(request):
    """
    summary: Get combined recommendation summary
    description: |
      Provide a high-level recommendation summary and surface the latest session notes location.
    tags:
      - Clinical
    """
    serializer = GetRecommendationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    # Compose a generic instruction to fetch a RAG summary based on session context
    question = "Provide a concise clinical recommendation summary based on general adult primary care guidelines."
    answer, citations, safety = _CLINICAL.recommend(data["session_id"], question, top_k=3)
    # Notes location
    location_type, path_or_id = _PATIENT.get_notes_location(data["session_id"])
    resp = GetRecommendationResponseSerializer({
        "recommendation": answer,
        "session_notes_location": f"{location_type}:{path_or_id}",
        "safety": safety
    })
    return Response(resp.data, status=status.HTTP_200_OK)
