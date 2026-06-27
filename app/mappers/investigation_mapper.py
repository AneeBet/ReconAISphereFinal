from app.schemas.investigation import (
    InvestigationOverview,
    TimelineItem,
    RelatedTransaction,
    CaseComment,
    CaseAttachment,
    InvestigationCaseResponse
)


class InvestigationMapper:

    @staticmethod
    def to_response(case):

        exception = case.exception
        reconciliation = exception.reconciliation_result
        payment = reconciliation.payment_transaction
        bank = reconciliation.bank_transaction

        return InvestigationCaseResponse(

            overview=InvestigationOverview(

                id=case.id,

                case_number=case.case_number,

                title=case.title,

                description=case.description,

                priority=case.priority.value,

                owner=(
                    f"{case.owner.first_name} {case.owner.last_name}"
                    if case.owner else None
                ),

                status=case.status.value,

                due_date=case.due_date,

                created_at=case.created_at

            ),

            ai_explanation=(
                case.ai_insights[0].explanation
                if case.ai_insights
                else None
            ),

            ai_recommendation=(
                case.ai_insights[0].recommendation
                if case.ai_insights
                else None
            ),

            confidence_score=(
                float(case.ai_insights[0].confidence)
                if case.ai_insights
                else None
            ),

            related_transactions=[

                RelatedTransaction(

                    payment_reference=payment.transaction_reference,

                    bank_reference=(
                        bank.transaction_reference
                        if bank else None
                    ),

                    payment_amount=float(payment.amount),

                    bank_amount=(
                        float(bank.amount)
                        if bank else None
                    ),

                    difference=(
                        float(payment.amount - bank.amount)
                        if bank else None
                    )

                )

            ],

            timeline=[

                TimelineItem(

                    changed_at=item.created_at,

                    changed_by=f"{item.changed_by.first_name} {item.changed_by.last_name}",

                    from_status=(
                        item.from_status.value
                        if item.from_status else None
                    ),

                    to_status=item.to_status.value,

                    remarks=item.remarks

                )

                for item in case.workflow_history

            ],

            comments=[

                CaseComment(

                    id=comment.id,

                    user=f"{comment.user.first_name} {comment.user.last_name}",

                    comment=comment.comment,

                    created_at=comment.created_at

                )

                for comment in case.comments

            ],

            attachments=[

                CaseAttachment(

                    id=file.id,

                    file_name=file.file_name,

                    blob_url=file.blob_url,

                    uploaded_by=f"{file.uploaded_by.first_name} {file.uploaded_by.last_name}",

                    uploaded_at=file.created_at

                )

                for file in case.attachments

            ]

        )
