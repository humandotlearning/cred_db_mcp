import gradio as gr
from .tools import (
    sync_provider_from_npi,
    add_or_update_credential,
    list_expiring_credentials,
    get_provider_snapshot
)

def main():
    """
    Main entry point for the Gradio MCP server.
    """
    # Create the Gradio interface
    # We use a TabbedInterface to organize the tools if accessed via UI,
    # but primarily they are exposed as MCP tools.

    # Tool 1: sync_provider_from_npi
    iface_sync = gr.Interface(
        fn=sync_provider_from_npi,
        inputs=[gr.Textbox(label="NPI")],
        outputs=gr.JSON(label="Provider Data"),
        description="Syncs a provider's data from the NPI registry.",
        allow_flagging="never"
    )

    # Tool 2: add_or_update_credential
    iface_add_cred = gr.Interface(
        fn=add_or_update_credential,
        inputs=[
            gr.Number(label="Provider ID", precision=0),
            gr.Textbox(label="Type"),
            gr.Textbox(label="Issuer"),
            gr.Textbox(label="Number"),
            gr.Textbox(label="Expiry Date (YYYY-MM-DD)"),
        ],
        outputs=gr.JSON(label="Credential Data"),
        description="Adds or updates a credential for a provider.",
        allow_flagging="never"
    )

    # Tool 3: list_expiring_credentials
    iface_expiring = gr.Interface(
        fn=list_expiring_credentials,
        inputs=[
            gr.Number(label="Window Days", precision=0),
            gr.Textbox(label="Department", value=None),
            gr.Textbox(label="Location", value=None),
        ],
        outputs=gr.JSON(label="Expiring Credentials"),
        description="Lists credentials expiring within a certain number of days.",
        allow_flagging="never"
    )

    # Tool 4: get_provider_snapshot
    iface_snapshot = gr.Interface(
        fn=get_provider_snapshot,
        inputs=[
            gr.Number(label="Provider ID", precision=0, value=None),
            gr.Textbox(label="NPI", value=None),
        ],
        outputs=gr.JSON(label="Provider Snapshot"),
        description="Gets a snapshot of a provider's data including credentials and alerts.",
        allow_flagging="never"
    )

    demo = gr.TabbedInterface(
        [iface_sync, iface_add_cred, iface_expiring, iface_snapshot],
        ["Sync Provider", "Add/Update Credential", "List Expiring", "Provider Snapshot"]
    )

    # Launch with mcp_server=True to enable MCP endpoints
    demo.launch(mcp_server=True)

if __name__ == "__main__":
    main()
