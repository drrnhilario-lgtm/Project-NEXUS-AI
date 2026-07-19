"""Theme-aware CSS for the Streamlit dashboard."""

import streamlit as st


def apply_theme() -> None:
    """Inject the shared NEXUS AI design system."""
    st.markdown(
        """
        <style>
          :root {
            --space-1:.35rem;--space-2:.65rem;--space-3:1rem;--space-4:1.5rem;
            --radius-sm:.6rem;--radius-md:.9rem;--radius-lg:1.35rem;
            --surface:var(--secondary-background-color);--text:var(--text-color);
            --border:color-mix(in srgb,var(--text-color) 16%,transparent);
            --muted:color-mix(in srgb,var(--text-color) 68%,transparent);
            --accent:var(--primary-color);
            --soft:color-mix(in srgb,var(--primary-color) 12%,var(--background-color));
            --shadow:0 6px 18px color-mix(in srgb,#000 10%,transparent);
            --space-section:clamp(1.35rem,3vw,2.25rem);--heading-page:clamp(1.65rem,3vw,2.15rem);
            --heading-section:clamp(1.15rem,2vw,1.4rem);--panel-bg:var(--secondary-background-color);
          }
          .block-container{max-width:1240px;padding-top:2rem;padding-bottom:2rem}
          .nexus-hero{padding:clamp(1.75rem,4vw,3.25rem);border-radius:var(--radius-lg);
            background:linear-gradient(135deg,#101f4f,#2855d9 70%,#3876ef);color:#fff;
            box-shadow:0 18px 42px rgba(15,31,79,.24);margin-bottom:1rem}
          .nexus-hero .brand{font-size:.78rem;font-weight:800;letter-spacing:.16em;opacity:.76}
          .nexus-hero h1{color:#fff;margin:.35rem 0 .3rem;font-size:clamp(2.15rem,5vw,3.65rem)}
          .nexus-hero .subtitle{margin:0;font-size:clamp(1rem,2vw,1.2rem);opacity:.9}
          .hero-badges{display:flex;flex-wrap:wrap;gap:.55rem;margin-top:1.25rem}
          .hero-badge{padding:.42rem .72rem;border:1px solid rgba(255,255,255,.2);
            border-radius:999px;background:rgba(255,255,255,.11);font-size:.78rem;font-weight:750}
          .nexus-hero.compact{padding:clamp(1rem,2.5vw,1.65rem);margin-bottom:.7rem}
          .nexus-hero.compact h1{font-size:clamp(1.7rem,3.5vw,2.45rem);margin:.2rem 0}
          .nexus-hero.compact .hero-badges{margin-top:.7rem}
          h2{font-size:var(--heading-page)} h3{font-size:var(--heading-section)}
          [data-testid="stSidebar"] [role="radiogroup"] label{border-radius:var(--radius-sm);padding:.25rem .45rem}
          [data-testid="stSidebar"] [role="radiogroup"] label:hover{background:var(--soft)}
          [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:var(--accent);color:#fff;font-weight:750}
          [data-testid="stButton"]>button{min-height:3rem;border-radius:var(--radius-md);font-weight:800;box-shadow:var(--shadow)}
          [data-testid="stButton"]>button:hover{filter:brightness(1.08)}
          [data-baseweb="tab-list"]{gap:var(--space-2);margin-bottom:var(--space-3)}
          [data-baseweb="tab"]{padding:.65rem .85rem;border-radius:var(--radius-sm) var(--radius-sm) 0 0}
          [data-baseweb="tab"][aria-selected="true"]{color:var(--text);background:var(--soft);font-weight:800}
          .section-label{margin:1.5rem 0 .6rem;font-weight:750;color:var(--text)}
          .input-intro,.score-summary,.evidence-line,.empty-inline{color:var(--muted)}
          .dashboard-heading{display:flex;align-items:end;justify-content:space-between;gap:1.5rem;
            margin-top:2rem;padding:1.4rem 1.5rem;border:1px solid var(--border);
            border-radius:var(--radius-md);background:var(--surface)}
          .ats-heading{display:flex;align-items:end;justify-content:space-between;gap:1.5rem;
            padding:1.2rem 1.4rem;margin:.5rem 0 1rem;border:1px solid var(--border);
            border-radius:var(--radius-md);background:var(--soft)}
          .section-kicker{color:var(--muted);font-size:.75rem;font-weight:800;letter-spacing:.12em}
          .score-display{color:var(--text);font-size:clamp(2.6rem,6vw,4.2rem);font-weight:850;line-height:1}
          .status-badge,.priority-badge{display:inline-block;padding:.25rem .65rem;border-radius:999px;font-size:.72rem;font-weight:850}
          .status-badge{color:var(--text);background:var(--soft);border:1px solid var(--border)}
          .priority-high{color:#7f1d1d;background:#fecaca}.priority-medium{color:#78350f;background:#fde68a}.priority-low{color:#14532d;background:#bbf7d0}
          .metric-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.85rem;margin:1rem 0 1.5rem}
          .metric-card{display:flex;flex-direction:column;justify-content:center;min-height:6.35rem;
            padding:1rem;border:1px solid var(--border);border-radius:var(--radius-md);background:var(--surface);box-shadow:var(--shadow)}
          .metric-value{color:var(--text);font-size:1.8rem;font-weight:850}.metric-label{color:var(--muted);font-size:.82rem}
          .metric-subtitle{color:var(--muted);font-size:.75rem;line-height:1.35;margin-top:.35rem}
          .executive-metrics{grid-template-columns:repeat(5,minmax(0,1fr))}.executive-metrics .metric-value{overflow-wrap:anywhere;font-size:clamp(1.25rem,2.2vw,1.8rem)}
          .executive-insight{margin:var(--space-section) 0;padding:1.15rem 1.25rem;border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:var(--radius-md);background:var(--panel-bg);box-shadow:var(--shadow)}
          .executive-insight p{max-width:78ch;margin:.45rem 0 .75rem;color:var(--text);line-height:1.65}.insight-chips{display:flex;flex-wrap:wrap;gap:.45rem}.insight-chip,.download-status{padding:.25rem .55rem;border:1px solid var(--border);border-radius:999px;background:var(--soft);color:var(--text);font-size:.72rem;font-weight:750}
          .polished-card{height:100%;padding:1rem;border:1px solid var(--border);border-radius:var(--radius-md);background:var(--surface);box-shadow:var(--shadow);color:var(--text)}
          .priority-card{min-height:17rem}.priority-card-head{display:flex;align-items:center;justify-content:space-between}.priority-card h3{overflow-wrap:anywhere}.priority-card p,.support-line{color:var(--muted);line-height:1.5}.support-line{font-size:.82rem;margin-top:.55rem}
          .action-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.65rem}.action-card{display:flex;gap:.75rem;align-items:flex-start;padding:.85rem;border:1px solid var(--border);border-radius:var(--radius-sm);background:var(--surface)}.action-card span{display:block;color:var(--muted);font-size:.75rem;margin-top:.2rem}.action-check{display:grid!important;place-items:center;flex:0 0 1.7rem;height:1.7rem;border-radius:50%;background:var(--soft);color:var(--accent)!important;font-weight:850}
          .metadata-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.6rem}.metadata-grid div{padding:.8rem;border:1px solid var(--border);border-radius:var(--radius-sm);background:var(--surface)}.metadata-grid span,.metadata-grid strong{display:block}.metadata-grid span{color:var(--muted);font-size:.72rem}.metadata-grid strong{margin-top:.2rem;overflow-wrap:anywhere}
          .empty-state-card{display:flex;align-items:flex-start;gap:1rem;max-width:760px;margin:1.25rem auto;padding:1.1rem 1.2rem;border:1px solid var(--border);border-radius:var(--radius-md);background:var(--surface);box-shadow:var(--shadow)}.empty-state-card h3,.empty-state-card p{margin:.1rem 0}.empty-state-card p{color:var(--muted);line-height:1.55}.empty-icon{font-size:1.5rem}.empty-action{margin-top:.55rem;color:var(--accent);font-weight:750}
          .download-card{min-height:10rem;margin-bottom:.55rem}.download-card h3{margin:.55rem 0 .3rem}.download-card p{color:var(--muted);line-height:1.5}
          .skill-item{margin:.45rem 0;padding:.8rem;border:1px solid var(--border);border-radius:var(--radius-sm);background:var(--surface);color:var(--text);box-shadow:var(--shadow)}
          .skill-matched{border-left:3px solid #22c55e}.skill-missing{border-left:3px solid #ef4444}
          .skill-heading{display:flex;align-items:center;justify-content:space-between;gap:.6rem}.evidence-line{font-size:.83rem;margin-top:.35rem}
          .recommendation-card{display:grid;grid-template-columns:auto 1fr;gap:.9rem;margin:.8rem 0;padding:1rem;border:1px solid var(--border);border-radius:var(--radius-md);background:var(--surface);color:var(--text);box-shadow:var(--shadow)}
          .recommendation-number{display:grid;place-items:center;width:2rem;height:2rem;border-radius:50%;background:var(--accent);color:#fff;font-weight:850}
          .recommendation-title{font-weight:800}.recommendation-card p,.roadmap-card p,.section-card p{color:var(--muted)}
          .roadmap-card,.section-card{padding:1rem;border:1px solid var(--border);border-radius:var(--radius-md);background:var(--soft);color:var(--text)}
          .roadmap-card{min-height:9rem}.roadmap-card h3,.section-card h3{margin:0 0 .5rem;color:var(--text)}
          .section-card{display:flex;gap:1rem;margin-top:1rem}.section-card-icon{font-size:1.4rem;color:var(--accent)}
          .section-card ol{margin:.75rem 0 0;padding-left:1.2rem;color:var(--muted)}
          .ats-category{display:flex;align-items:center;justify-content:space-between;gap:1rem;
            margin:.45rem 0;padding:.75rem .9rem;border:1px solid var(--border);
            border-radius:var(--radius-sm);background:var(--surface);color:var(--text)}
          .ats-category strong{white-space:nowrap;color:var(--accent)}
          .executive-summary{margin:.75rem 0 1rem;padding:1rem 1.1rem;
            border-left:3px solid var(--accent);border-radius:var(--radius-sm);
            background:var(--soft);color:var(--text);line-height:1.65}
          .intelligence-metrics{grid-template-columns:repeat(5,1fr)}
          .intelligence-hero{display:grid;grid-template-columns:minmax(180px,.7fr) 2fr;
            align-items:center;gap:1.5rem;margin:.75rem 0 1rem;padding:1.4rem;
            border:1px solid var(--border);border-radius:var(--radius-md);
            background:var(--surface);color:var(--text);box-shadow:var(--shadow)}
          .intelligence-hero p{margin:0;color:var(--muted);line-height:1.65}
          .intelligence-card{margin:.65rem 0;padding:1rem;border:1px solid var(--border);
            border-radius:var(--radius-md);background:var(--surface);color:var(--text);
            box-shadow:var(--shadow)}
          .intelligence-card p{color:var(--muted);line-height:1.55}
          .improvement-card{border-left:3px solid var(--accent)}
          .source-label{display:inline-block;margin-top:.35rem;color:var(--muted);
            font-size:.72rem;font-weight:750;letter-spacing:.06em;text-transform:uppercase}
          .priority-card{min-height:15rem}.priority-rank{display:grid;place-items:center;
            width:2rem;height:2rem;border-radius:50%;background:var(--accent);color:#fff;font-weight:850}
          .roadmap-phase{min-height:32rem}.phase-label{color:var(--accent);font-size:.72rem;
            font-weight:850;letter-spacing:.08em;text-transform:uppercase}
          .duration{margin:.65rem 0;padding:.45rem .6rem;border-radius:var(--radius-sm);
            background:var(--soft);color:var(--muted);font-size:.78rem}
          .nexus-footer{margin-top:2.5rem;padding-top:1.2rem;border-top:1px solid var(--border);color:var(--muted);text-align:center;font-size:.82rem}
          @media(max-width:800px){.metric-grid,.intelligence-metrics,.executive-metrics,.metadata-grid{grid-template-columns:repeat(2,1fr)}
            .dashboard-heading{align-items:flex-start;flex-direction:column}
            .intelligence-hero{grid-template-columns:1fr}.roadmap-phase,.priority-card{min-height:auto}}
          @media(max-width:520px){.block-container{padding-left:1rem;padding-right:1rem}.skill-heading{align-items:flex-start;flex-direction:column}.action-grid,.metadata-grid{grid-template-columns:1fr}.nexus-hero{border-radius:var(--radius-md)}}
        </style>
        """,
        unsafe_allow_html=True,
    )
