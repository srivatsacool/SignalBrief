# signalbrief_builder package
import nbformat as nbf

def md(content):
    return nbf.v4.new_markdown_cell(content.strip())

def code(content):
    return nbf.v4.new_code_cell(content.strip())

def card_pre(cell_num, tlp_tag, what, why, method, assumptions):
    """
    Renders a publication-grade pre-execution Algorithmic Directive Card.
    Dual-adaptive: explicit #0F172A text on #F8FAFC surface with #0284C7 accent ribbon.
    Guarantees 100% text visibility in any JupyterLab/VS Code theme.
    """
    return f"""<div style="background-color: #F8FAFC; border: 1px solid #CBD5E1; border-left: 5px solid #0284C7; border-radius: 6px; padding: 16px 20px; margin: 14px 0; color: #0F172A; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid #E2E8F0; padding-bottom: 6px;">
        <span style="font-weight: 800; color: #0284C7; font-size: 13.5px; text-transform: uppercase; letter-spacing: 0.5px;">📋 Algorithmic Directive &bull; Code Cell {cell_num}</span>
        <span style="background-color: #E0F2FE; color: #0369A1; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 700;">{tlp_tag}</span>
    </div>
    <p style="margin: 6px 0; font-size: 13.5px; line-height: 1.55; color: #0F172A;"><strong style="color: #0369A1;">WHAT ARE WE DOING:</strong> {what}</p>
    <p style="margin: 6px 0; font-size: 13.5px; line-height: 1.55; color: #0F172A;"><strong style="color: #0369A1;">WHY ARE WE DOING IT:</strong> {why}</p>
    <div style="font-size: 12px; color: #334155; border-top: 1px solid #E2E8F0; padding-top: 8px; margin-top: 8px; background-color: #F1F5F9; padding: 6px 10px; border-radius: 4px;">
        <strong>Method / Algorithm:</strong> <code style="color: #0F172A; background-color: #E2E8F0; padding: 1px 4px; border-radius: 3px;">{method}</code> &nbsp;|&nbsp; <strong>Assumptions:</strong> {assumptions}
    </div>
</div>"""

def card_post(means, interpret, look_for, limitations, business):
    """
    Renders a publication-grade post-execution Executive Interpretation Card.
    Dual-adaptive: explicit #064E3B text on #F0FDF4 surface with #059669 accent ribbon.
    Guarantees 100% text visibility in any JupyterLab/VS Code theme.
    """
    return f"""<div style="background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 5px solid #059669; border-radius: 6px; padding: 16px 20px; margin: 14px 0; color: #064E3B; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid #DCFCE7; padding-bottom: 6px;">
        <span style="font-weight: 800; color: #059669; font-size: 13.5px; text-transform: uppercase; letter-spacing: 0.5px;">💡 Executive Interpretation & Empirical Insights</span>
        <span style="background-color: #DCFCE7; color: #15803D; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 700;">Verified Output</span>
    </div>
    <p style="margin: 6px 0; font-size: 13.5px; line-height: 1.55; color: #064E3B;"><strong style="color: #047857;">WHAT THE OUTPUT MEANS:</strong> {means}</p>
    <p style="margin: 6px 0; font-size: 13.5px; line-height: 1.55; color: #064E3B;"><strong style="color: #047857;">HOW TO INTERPRET:</strong> {interpret}</p>
    <p style="margin: 6px 0; font-size: 13.5px; line-height: 1.55; color: #064E3B;"><strong style="color: #047857;">WHAT TO LOOK FOR:</strong> {look_for}</p>
    <div style="font-size: 12px; color: #166534; border-top: 1px solid #DCFCE7; padding-top: 8px; margin-top: 8px; background-color: #DCFCE7; padding: 6px 10px; border-radius: 4px;">
        <strong>Strategic Business Action:</strong> {business} &nbsp;|&nbsp; <strong>Caution / Boundary:</strong> {limitations}
    </div>
</div>"""

def section_hero(section_num, section_title, session_tag, co_tag, desc):
    """
    Renders a striking Section Header Card with deep slate surface and electric cyan accent.
    """
    return f"""<div style="background-color: #0B1120; border: 1px solid #1E293B; border-left: 6px solid #38BDF8; border-radius: 8px; padding: 20px 24px; margin: 24px 0 16px 0; color: #F8FAFC; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <span style="color: #38BDF8; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">SECTION {section_num:02d}</span>
        <div>
            <span style="background-color: #1E293B; color: #94A3B8; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-right: 6px;">{session_tag}</span>
            <span style="background-color: #0369A1; color: #FFFFFF; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 700;">{co_tag}</span>
        </div>
    </div>
    <h2 style="color: #FFFFFF; margin: 6px 0 10px 0; font-size: 22px; font-weight: 800;">{section_title}</h2>
    <p style="color: #CBD5E1; margin: 0; font-size: 14px; line-height: 1.5;">{desc}</p>
</div>"""
