import mongoengine as me


class OtpAccountActiveModel(me.Document):
    otp = me.StringField(required=True)
    created_at = me.IntField(required=True)
    updated_at = me.IntField(required=True)

    account_active = me.ReferenceField(
        "AccountActiveModel", reverse_delete_rule=me.CASCADE
    )

    meta = {"collection": "otp_account_active"}
