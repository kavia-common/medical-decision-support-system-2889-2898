from django.core.management.base import BaseCommand
from api.agents import PatientAgent, ClinicalAgent
from api.rag_service import RAGIndex


class Command(BaseCommand):
    help = "Run a CLI demo for the medical decision support backend."

    # PUBLIC_INTERFACE
    def handle(self, *args, **options):
        """
        This CLI demo walks through:
        - Patient chat interaction
        - Clinical recommendation via RAG
        - Report refinement
        """
        session_id = "demo-session"
        rag = RAGIndex(base_dir=".")
        patient = PatientAgent()
        clinical = ClinicalAgent(rag)

        self.stdout.write(self.style.SUCCESS("Starting CLI demo..."))
        msg = "I have had a persistent cough for two weeks and some mild fever."
        self.stdout.write(self.style.NOTICE(f"Patient: {msg}"))
        reply, safety = patient.reply(session_id, msg)
        self.stdout.write(self.style.SUCCESS(f"Agent: {reply}"))
        self.stdout.write(self.style.HTTP_INFO(f"Safety: {safety}"))

        q = "What are recommended steps for subacute cough evaluation in adults?"
        self.stdout.write(self.style.NOTICE(f"Clinical Question: {q}"))
        answer, citations, safety2 = clinical.recommend(session_id, q, top_k=3)
        self.stdout.write(self.style.SUCCESS(f"Recommendation:\n{answer}"))
        self.stdout.write(self.style.HTTP_INFO(f"Citations: {citations}"))
        self.stdout.write(self.style.HTTP_INFO(f"Safety: {safety2}"))

        report_text = """
        Chest X-Ray
        Impression: No acute cardiopulmonary abnormality identified.
        Recommendation: Correlate findings clinically if symptoms persist.
        """
        refined, safety3 = clinical.refine_report(session_id, report_text)
        self.stdout.write(self.style.SUCCESS(f"Refined Report:\n{refined}"))
        self.stdout.write(self.style.HTTP_INFO(f"Safety: {safety3}"))

        self.stdout.write(self.style.SUCCESS("CLI demo complete."))
