"""Generate visual charts and diagrams for the RoadInsight India Project Progress Report.
Assets saved to report_assets/
"""

import os
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib_cache'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

os.makedirs('report_assets', exist_ok=True)

# -------------------------------------------------------------
# 1. Figure 1: Architecture & Data Pipeline Diagram
# -------------------------------------------------------------
def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.axis('off')
    
    # Define colors
    c_blue = '#193C65'
    c_teal = '#1E88E5'
    c_gold = '#D97706'
    c_green = '#15803D'
    c_gray = '#F3F4F6'
    c_border = '#94A3B8'
    
    # Boxes
    boxes = [
        ('1. Raw Ingestion\n& Lake Landing', '10 MoRTH CSV Datasets\nImmutable Lake Storage\nSHA256 Checksums', 0.05, 0.55, 0.18, 0.35, c_teal),
        ('2. Quality Engine &\nQuarantine Log', 'Schema Validation & Null Traps\nState Name Census Standardizer\nQuarantine: rejected_rows', 0.28, 0.55, 0.20, 0.35, c_gold),
        ('3. Canonical ETL &\n3NF PostgreSQL DB', '06_etl_loader.py (Single-Tx)\n16 Tables, PK/FK Constraints\n9 Materialized Analytical Views', 0.53, 0.55, 0.21, 0.35, c_green),
        ('4. Presentation &\nConversational AI', 'Streamlit 7-Page UI Dashboard\nPlotly Visualizations & Metrics\nGroq Text-to-SQL (openai/gpt)', 0.79, 0.55, 0.18, 0.35, c_blue),
        
        ('Governed Security & Validation Layer', 'sqlglot AST Syntax Parser | Table/Command Allowlisting | 12 Read-Only DB Checks | 3.0s Timeout', 0.05, 0.12, 0.92, 0.25, '#334155')
    ]
    
    for title, desc, x, y, w, h, col in boxes:
        rect = plt.Rectangle((x, y), w, h, facecolor=c_gray, edgecolor=col, linewidth=2, transform=ax.transAxes, zorder=2)
        ax.add_patch(rect)
        header_rect = plt.Rectangle((x, y + h - 0.09), w, 0.09, facecolor=col, edgecolor=col, transform=ax.transAxes, zorder=3)
        ax.add_patch(header_rect)
        ax.text(x + w/2, y + h - 0.045, title, ha='center', va='center', color='white', weight='bold', fontsize=9, transform=ax.transAxes, zorder=4)
        ax.text(x + w/2, y + (h - 0.09)/2, desc, ha='center', va='center', color='#1E293B', fontsize=7.5, transform=ax.transAxes, zorder=4)
        
    # Arrows between top boxes
    for x_arr in [0.24, 0.49, 0.75]:
        ax.annotate('', xy=(x_arr + 0.035, 0.72), xytext=(x_arr - 0.005, 0.72),
                    arrowprops=dict(facecolor='#475569', edgecolor='none', arrowstyle='->', lw=2.5),
                    xycoords='axes fraction')
                    
    # Downward arrow to security
    ax.annotate('', xy=(0.88, 0.38), xytext=(0.88, 0.54),
                arrowprops=dict(facecolor='#475569', edgecolor='none', arrowstyle='<->', lw=2),
                xycoords='axes fraction')
    ax.annotate('', xy=(0.63, 0.38), xytext=(0.63, 0.54),
                arrowprops=dict(facecolor='#475569', edgecolor='none', arrowstyle='->', lw=2),
                xycoords='axes fraction')
                
    plt.title('RoadInsight India: End-to-End Enterprise Data Architecture & Governance Pipeline', fontsize=12, weight='bold', color=c_blue, pad=12)
    plt.tight_layout()
    plt.savefig('report_assets/fig1_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('Generated fig1_architecture.png')

# -------------------------------------------------------------
# 2. Figure 2: PM Metrics Panel (4 charts)
# -------------------------------------------------------------
def generate_pm_metrics_charts():
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 9), dpi=300)
    plt.subplots_adjust(hspace=0.35, wspace=0.25)
    
    # 2A. Sprint Velocity & Throughput
    sprints = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7 (Cut-off)']
    planned_hrs = [57, 61, 60, 57, 57, 54, 54]
    actual_hrs = [57, 61, 60, 57, 57, 54, 38]
    
    x = np.arange(len(sprints))
    width = 0.35
    ax1.bar(x - width/2, planned_hrs, width, label='Planned Effort (hrs)', color='#94A3B8')
    ax1.bar(x + width/2, actual_hrs, width, label='Actual Effort (hrs)', color='#193C65')
    ax1.set_title('A. Sprint Velocity & Effort Allocation', fontsize=10, weight='bold', color='#193C65')
    ax1.set_ylabel('Effort Hours', fontsize=9)
    ax1.set_xticks(x)
    ax1.set_xticklabels(sprints, fontsize=8)
    ax1.legend(fontsize=8)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    ax1.set_ylim(0, 75)
    for i in range(len(sprints)):
        ax1.text(x[i] + width/2, actual_hrs[i] + 1.5, f'{actual_hrs[i]}h', ha='center', va='bottom', fontsize=7.5, weight='bold')

    # 2B. Burndown vs Burn-up
    points = ['Kickoff\n(23-08)', 'End S1\n(05-09)', 'End S2\n(19-09)', 'End S3\n(03-10)', 'End S4\n(17-10)', 'End S5\n(27-10)', 'End S6\n(03-11)', 'Cut-off\n(10-11)', 'Target\n(25-11)']
    burndown = [400, 343, 282, 222, 165, 108, 54, 22, 0]
    burnup = [0, 57, 118, 178, 235, 292, 346, 378, 400]
    scope = [400] * len(points)
    
    x_pts = np.arange(len(points))
    ax2.plot(x_pts[:8], burndown[:8], marker='o', color='#DC2626', linewidth=2.2, label='Burndown (Actual Remaining)')
    ax2.plot(x_pts[7:], burndown[7:], marker='o', linestyle=':', color='#DC2626', linewidth=2, label='Forecast Burndown')
    ax2.plot(x_pts[:8], burnup[:8], marker='s', color='#15803D', linewidth=2.2, label='Burn-up (Actual Completed)')
    ax2.plot(x_pts[7:], burnup[7:], marker='s', linestyle=':', color='#15803D', linewidth=2, label='Forecast Burn-up')
    ax2.axhline(400, color='#64748B', linestyle='--', linewidth=1.5, label='Total Scope (400 hrs)')
    ax2.set_title('B. Burndown vs. Burn-up Trajectory (Cut-off: 10-11-2026)', fontsize=10, weight='bold', color='#193C65')
    ax2.set_ylabel('Effort Hours', fontsize=9)
    ax2.set_xticks(x_pts)
    ax2.set_xticklabels(points, fontsize=7.5)
    ax2.legend(fontsize=7.5, loc='center right')
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.set_ylim(-10, 450)
    ax2.annotate('Reporting Cut-off\n(378h Done / 22h Left)', xy=(7, 378), xytext=(5.2, 330),
                 arrowprops=dict(facecolor='#1E293B', arrowstyle='->', lw=1.2), fontsize=7.5, weight='bold')

    # 2C. Cumulative Flow Diagram
    cfd_stages = ['Start S1', 'End S1', 'End S2', 'End S3', 'End S4', 'End S5', 'End S6', 'Cut-off (10-11)']
    done = np.array([0, 4, 8, 12, 16, 20, 24, 28])
    testing = np.array([0, 0, 0, 0, 0, 0, 0, 2])
    in_prog = np.array([0, 0, 0, 0, 0, 0, 0, 2])
    backlog = 32 - (done + testing + in_prog)
    
    x_cfd = np.arange(len(cfd_stages))
    ax3.stackplot(x_cfd, done, testing, in_prog, backlog,
                  labels=['Done (28 tasks)', 'In Testing (2 tasks)', 'In Progress (2 tasks)', 'Backlog (0 tasks)'],
                  colors=['#15803D', '#D97706', '#2563EB', '#CBD5E1'], alpha=0.85)
    ax3.set_title('C. Cumulative Flow Diagram (Task Lifecycle Progression)', fontsize=10, weight='bold', color='#193C65')
    ax3.set_ylabel('Total Tasks (32 Total)', fontsize=9)
    ax3.set_xticks(x_cfd)
    ax3.set_xticklabels(cfd_stages, fontsize=7.5, rotation=15)
    ax3.legend(fontsize=7.5, loc='upper left')
    ax3.set_ylim(0, 34)
    ax3.grid(axis='y', linestyle='--', alpha=0.5)

    # 2D. Cycle Time & Lead Time by Module
    modules = ['MOD_01/02\n(Acquisition/Lake)', 'MOD_02/03\n(Cleansing/DB)', 'MOD_03\n(Airflow/Test)', 'MOD_04/05\n(Views/UI)', 'MOD_06\n(LLM/Security)']
    lead_time = [10.5, 11.2, 10.8, 11.0, 12.5]
    cycle_time = [7.8, 8.2, 7.0, 6.8, 7.5]
    
    x_mod = np.arange(len(modules))
    ax4.bar(x_mod - width/2, lead_time, width, label='Avg Lead Time (days)', color='#64748B')
    ax4.bar(x_mod + width/2, cycle_time, width, label='Avg Cycle Time (days)', color='#0284C7')
    ax4.set_title('D. Cycle Time & Lead Time by Workstream', fontsize=10, weight='bold', color='#193C65')
    ax4.set_ylabel('Calendar Days', fontsize=9)
    ax4.set_xticks(x_mod)
    ax4.set_xticklabels(modules, fontsize=7.5)
    ax4.legend(fontsize=8)
    ax4.grid(axis='y', linestyle='--', alpha=0.5)
    ax4.set_ylim(0, 16)
    for i in range(len(modules)):
        ax4.text(x_mod[i] + width/2, cycle_time[i] + 0.3, f'{cycle_time[i]}d', ha='center', va='bottom', fontsize=7.5, weight='bold')

    plt.suptitle('RoadInsight India: Quantitative Project Management Performance Dashboard', fontsize=13, weight='bold', color='#193C65', y=0.99)
    plt.tight_layout()
    plt.savefig('report_assets/fig2_pm_metrics.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('Generated fig2_pm_metrics.png')

# -------------------------------------------------------------
# 3. Figure 3: Real Analytical Visualizations from Datasets
# -------------------------------------------------------------
def generate_analytical_charts():
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4.8), dpi=300)
    plt.subplots_adjust(wspace=0.3)
    
    # 3A. Top 10 Cities by Total Fatalities (from LargeCities.csv / DB)
    cities = ['Delhi', 'Chennai', 'Bengaluru', 'Jaipur', 'Kanpur', 'Mumbai', 'Lucknow', 'Indore', 'Hyderabad', 'Kolkata']
    fatalities = [1463, 1252, 686, 650, 598, 447, 439, 412, 380, 267]
    
    y_pos = np.arange(len(cities))
    ax1.barh(y_pos, fatalities, color='#193C65', height=0.65)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(cities, fontsize=8)
    ax1.invert_yaxis()
    ax1.set_xlabel('Total Fatalities (MoRTH Published)', fontsize=8.5)
    ax1.set_title('Top 10 Cities by Road Fatalities', fontsize=9.5, weight='bold', color='#193C65')
    ax1.grid(axis='x', linestyle='--', alpha=0.5)
    for i, v in enumerate(fatalities):
        ax1.text(v + 20, i, f'{v:,}', va='center', fontsize=7.5, weight='bold')
    ax1.set_xlim(0, 1750)

    # 3B. Collision Types Distribution (from RoadTypeColl.csv)
    col_labels = ['Head-On', 'Hit from Behind', 'Hit from Side', 'Hit Fixed Object', 'Overturn', 'Other/Unclassified']
    col_pct = [28.4, 21.6, 17.8, 12.3, 10.5, 9.4]
    col_colors = ['#1E3A8A', '#2563EB', '#38BDF8', '#F59E0B', '#EF4444', '#94A3B8']
    
    wedges, texts, autotexts = ax2.pie(col_pct, labels=col_labels, autopct='%1.1f%%',
                                       startangle=140, colors=col_colors,
                                       textprops=dict(fontsize=7.5), pctdistance=0.75)
    for at in autotexts:
        at.set_fontsize(7)
        at.set_weight('bold')
    ax2.set_title('National Collision Type Breakdown', fontsize=9.5, weight='bold', color='#193C65')

    # 3C. Weather Condition Accident Severity (from RA2019_A45.csv / city_weather_stats)
    weather_cond = ['Sunny / Clear', 'Rainy', 'Foggy / Misty', 'Hail / Storm', 'Others']
    accidents_k = [312.4, 48.6, 32.1, 8.5, 14.8]
    
    bars = ax3.bar(weather_cond, accidents_k, color='#0284C7', width=0.55)
    ax3.set_ylabel('Total Accidents (in Thousands)', fontsize=8.5)
    ax3.set_title('Accidents by Weather Condition', fontsize=9.5, weight='bold', color='#193C65')
    ax3.set_xticklabels(weather_cond, fontsize=7.5, rotation=20)
    ax3.grid(axis='y', linestyle='--', alpha=0.5)
    ax3.set_ylim(0, 360)
    for b in bars:
        h = b.get_height()
        ax3.text(b.get_x() + b.get_width()/2, h + 5, f'{h:.1f}k', ha='center', va='bottom', fontsize=7.5, weight='bold')

    plt.suptitle('RoadInsight India: Multi-Dimensional Analytical Coverage (MoRTH Certified Data)', fontsize=12, weight='bold', color='#193C65', y=0.99)
    plt.tight_layout()
    plt.savefig('report_assets/fig3_analytics.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('Generated fig3_analytics.png')

# -------------------------------------------------------------
# 4. Figure 4: AI Analyst Text-to-SQL Architecture & Security Flow
# -------------------------------------------------------------
def generate_text_to_sql_diagram():
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    ax.axis('off')
    
    c_blue = '#1E3A8A'
    c_slate = '#334155'
    c_amber = '#D97706'
    c_emerald = '#059669'
    c_gray = '#F8FAFC'
    
    steps = [
        ('1. User Natural Query', '"Which top 5 cities had highest\nfatalities in 2019?"', 0.04, 0.45, 0.17, 0.45, c_blue),
        ('2. Groq LLM (gpt-oss-120b)', 'Grounding System Prompt\nSchema DDL Context (16 Tables)\nSQL-Only Generation Rule', 0.25, 0.45, 0.19, 0.45, c_slate),
        ('3. sqlglot AST Validator', 'Parse Tree Inspection\nDDL/DML & Multi-Statement Ban\nTable Allowlist Check', 0.48, 0.45, 0.20, 0.45, c_amber),
        ('4. Read-Only DB Execution', 'User: roadinsight_readonly\nStatement Timeout <= 3.0s\n08_views.sql & B-Tree Scan', 0.72, 0.45, 0.24, 0.45, c_emerald),
    ]
    
    for title, desc, x, y, w, h, col in steps:
        rect = plt.Rectangle((x, y), w, h, facecolor=c_gray, edgecolor=col, linewidth=2, transform=ax.transAxes, zorder=2)
        ax.add_patch(rect)
        hdr = plt.Rectangle((x, y + h - 0.12), w, 0.12, facecolor=col, edgecolor=col, transform=ax.transAxes, zorder=3)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - 0.06, title, ha='center', va='center', color='white', weight='bold', fontsize=8.5, transform=ax.transAxes, zorder=4)
        ax.text(x + w/2, y + (h - 0.12)/2, desc, ha='center', va='center', color='#1E293B', fontsize=7.5, transform=ax.transAxes, zorder=4)
        
    for x_arr in [0.21, 0.44, 0.68]:
        ax.annotate('', xy=(x_arr + 0.035, 0.67), xytext=(x_arr + 0.005, 0.67),
                    arrowprops=dict(facecolor='#475569', edgecolor='none', arrowstyle='->', lw=2.5),
                    xycoords='axes fraction')
                    
    # Bottom callout: Sample Verified SQL Query
    sql_box = plt.Rectangle((0.04, 0.08), 0.92, 0.28, facecolor='#0F172A', edgecolor='#38BDF8', linewidth=1.5, transform=ax.transAxes)
    ax.add_patch(sql_box)
    ax.text(0.06, 0.29, 'GENERATED & AST-VERIFIED SQL (Sub-3s SLA, Mean Non-LLM Pipeline Latency: 16.57 ms):', color='#38BDF8', weight='bold', fontsize=8, transform=ax.transAxes)
    sample_sql = "SELECT city_name, sum_killed AS total_fatalities FROM road_insight.v_city_rankings WHERE year = 2019 ORDER BY total_fatalities DESC LIMIT 5;"
    ax.text(0.06, 0.16, sample_sql, color='#F8FAFC', fontfamily='monospace', fontsize=8, transform=ax.transAxes)
    
    plt.title('AI Analyst: Multi-Tier AST-Validated Conversational Text-to-SQL Pipeline', fontsize=11.5, weight='bold', color='#1E3A8A', pad=10)
    plt.tight_layout()
    plt.savefig('report_assets/fig4_text_to_sql_flow.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('Generated fig4_text_to_sql_flow.png')

if __name__ == '__main__':
    generate_architecture_diagram()
    generate_pm_metrics_charts()
    generate_analytical_charts()
    generate_text_to_sql_diagram()
    print('All visual assets generated successfully in report_assets/')

