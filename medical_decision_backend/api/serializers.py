from rest_framework import serializers


# PUBLIC_INTERFACE
class ChatRequestSerializer(serializers.Serializer):
    """Serializer for patient chat requests."""
    session_id = serializers.CharField(required=True, help_text="Unique session identifier to group messages.")
    message = serializers.CharField(required=True, help_text="Patient's message to the PatientAgent.")


# PUBLIC_INTERFACE
class ChatResponseSerializer(serializers.Serializer):
    """Serializer for patient chat responses."""
    reply = serializers.CharField(help_text="Assistant reply.")
    session_id = serializers.CharField(help_text="Session identifier.")
    safety = serializers.DictField(help_text="Safety signals and disclaimer.")


# PUBLIC_INTERFACE
class RecommendRequestSerializer(serializers.Serializer):
    """Serializer for recommendation requests to ClinicalAgent (RAG-powered)."""
    session_id = serializers.CharField(required=True, help_text="Session identifier to reference patient context.")
    question = serializers.CharField(required=True, help_text="Clinical question to retrieve recommendations for.")
    top_k = serializers.IntegerField(required=False, default=4, min_value=1, max_value=10, help_text="Number of RAG results.")


# PUBLIC_INTERFACE
class RecommendResponseSerializer(serializers.Serializer):
    """Serializer for recommendation responses."""
    answer = serializers.CharField(help_text="RAG-based recommendation.")
    citations = serializers.ListField(child=serializers.DictField(), help_text="List of source documents and scores.")
    safety = serializers.DictField(help_text="Safety signals and disclaimer.")


# PUBLIC_INTERFACE
class UploadReportSerializer(serializers.Serializer):
    """Serializer for uploading and refining a test report."""
    session_id = serializers.CharField(required=True)
    report_text = serializers.CharField(required=True, help_text="Raw report text content to refine.")


# PUBLIC_INTERFACE
class UploadReportResponseSerializer(serializers.Serializer):
    """Serializer for refined report response."""
    refined_report = serializers.CharField(help_text="Refined, structured version of the test report.")
    session_id = serializers.CharField(help_text="Session identifier.")
    safety = serializers.DictField(help_text="Safety signals and disclaimer.")


# PUBLIC_INTERFACE
class GetRecommendationRequestSerializer(serializers.Serializer):
    """Serializer for getting a combined recommendation summary."""
    session_id = serializers.CharField(required=True, help_text="Session identifier.")


# PUBLIC_INTERFACE
class GetRecommendationResponseSerializer(serializers.Serializer):
    """Serializer for combined recommendation response."""
    recommendation = serializers.CharField(help_text="Summarized recommendation.")
    session_notes_location = serializers.CharField(help_text="Where session notes are stored (OneDrive/local).")
    safety = serializers.DictField(help_text="Safety signals and disclaimer.")
