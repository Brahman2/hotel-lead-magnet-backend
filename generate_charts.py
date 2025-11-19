#!/usr/bin/env python3
"""
Generate Gantt Charts for Hotel Grader Implementation Timeline
Exports to PNG and SVG formats
"""

import plotly.figure_factory as ff
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

# Color scheme
COLORS = {
    'critical': '#EF4444',      # Red - Critical path
    'stretch': '#10B981',       # Green - Stretch goals
    'foundation': '#3B82F6',    # Blue - Foundation
    'analytics': '#8B5CF6',     # Purple - Analytics
    'automation': '#F59E0B',    # Orange - Automation
    'milestone': '#6B7280'      # Gray - Milestones
}

def create_prelaunch_gantt():
    """Create Pre-Launch Timeline Gantt Chart (Nov 19 - Feb 1)"""

    # Define tasks with dates
    tasks = [
        # Phase 0: Lead Generation
        dict(Task='Interactive Scanning: Images', Start='2025-11-19', Finish='2025-11-27', Resource='Phase 0', Type='critical'),
        dict(Task='Interactive Scanning: Reviews/Rankings', Start='2025-11-23', Finish='2025-11-29', Resource='Phase 0', Type='critical'),
        dict(Task='Enhanced Competitor Map', Start='2025-12-03', Finish='2025-12-08', Resource='Phase 0', Type='critical'),
        dict(Task='Competitor Ranking Summary', Start='2025-12-06', Finish='2025-12-09', Resource='Phase 0', Type='critical'),
        dict(Task='40-Metric Backend (AI Prompt)', Start='2025-12-03', Finish='2025-12-08', Resource='Phase 0', Type='critical'),
        dict(Task='40-Metric Backend (OTA Scraping)', Start='2025-12-08', Finish='2025-12-16', Resource='Phase 0', Type='critical'),

        # Phase 0: Stretch Goals
        dict(Task='🎁 Social Sharing Feature', Start='2025-12-10', Finish='2025-12-13', Resource='Stretch Goals', Type='stretch'),
        dict(Task='🎁 Live Chat Widget', Start='2025-12-13', Finish='2025-12-18', Resource='Stretch Goals', Type='stretch'),
        dict(Task='🎁 Voice-Over Narration', Start='2025-12-13', Finish='2025-12-17', Resource='Stretch Goals', Type='stretch'),
        dict(Task='🎁 AI Video Summary', Start='2025-12-13', Finish='2025-12-21', Resource='Stretch Goals', Type='stretch'),
        dict(Task='🎁 3D Visualization', Start='2025-12-13', Finish='2025-12-21', Resource='Stretch Goals', Type='stretch'),

        # Phase 1: SaaS Foundation
        dict(Task='Database Schema & Setup', Start='2025-12-17', Finish='2025-12-22', Resource='Phase 1', Type='foundation'),
        dict(Task='JWT Authentication', Start='2025-12-20', Finish='2025-12-26', Resource='Phase 1', Type='foundation'),
        dict(Task='User Registration/Login', Start='2025-12-24', Finish='2025-12-28', Resource='Phase 1', Type='foundation'),
        dict(Task='Main Dashboard UI', Start='2025-12-26', Finish='2026-01-02', Resource='Phase 1', Type='foundation'),
        dict(Task='Multi-Property Support', Start='2025-12-30', Finish='2026-01-04', Resource='Phase 1', Type='foundation'),

        # Phase 1: Analytics & Charts
        dict(Task='40-Metric Frontend Components', Start='2025-12-31', Finish='2026-01-10', Resource='Phase 1', Type='analytics'),
        dict(Task='Chart Library Integration', Start='2026-01-05', Finish='2026-01-11', Resource='Phase 1', Type='analytics'),
        dict(Task='Historical Data Storage', Start='2026-01-08', Finish='2026-01-13', Resource='Phase 1', Type='analytics'),
        dict(Task='Progress Tracking UI', Start='2026-01-10', Finish='2026-01-15', Resource='Phase 1', Type='analytics'),

        # Phase 1: Automation & Billing
        dict(Task='Automated Analysis Engine', Start='2026-01-14', Finish='2026-01-22', Resource='Phase 1', Type='automation'),
        dict(Task='Email Alerts & Notifications', Start='2026-01-18', Finish='2026-01-22', Resource='Phase 1', Type='automation'),
        dict(Task='Stripe Integration', Start='2026-01-20', Finish='2026-01-27', Resource='Phase 1', Type='automation'),
        dict(Task='Feature Management Interface', Start='2026-01-24', Finish='2026-01-28', Resource='Phase 1', Type='automation'),

        # Launch Prep
        dict(Task='🚀 Final QA & Testing', Start='2026-01-28', Finish='2026-01-30', Resource='Launch', Type='milestone'),
        dict(Task='🚀 Performance Optimization', Start='2026-01-29', Finish='2026-01-31', Resource='Launch', Type='milestone'),
        dict(Task='🚀 Documentation & Onboarding', Start='2026-01-30', Finish='2026-02-01', Resource='Launch', Type='milestone'),
    ]

    # Convert to DataFrame
    df = pd.DataFrame(tasks)

    # Create custom colors based on type
    colors = []
    for task_type in df['Type']:
        colors.append(COLORS[task_type])

    # Create Gantt chart
    fig = ff.create_gantt(
        df,
        colors=colors,
        index_col='Resource',
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        showgrid_y=True,
        title='Hotel Grader: Pre-Launch Timeline (Nov 19, 2025 → Feb 1, 2026)',
        bar_width=0.4,
        height=900,
        width=1600
    )

    # Update layout
    fig.update_layout(
        xaxis_title='Timeline',
        yaxis_title='Tasks',
        font=dict(size=11),
        title_font=dict(size=20, color='#1F2937'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            tickformat='%b %d\n%Y',
            dtick=7*24*60*60*1000,  # 1 week
            gridcolor='#E5E7EB'
        ),
        yaxis=dict(gridcolor='#E5E7EB'),
        showlegend=False
    )

    # Add milestone marker for launch using shape
    fig.add_shape(
        type="line",
        x0=datetime(2026, 2, 1),
        x1=datetime(2026, 2, 1),
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="red", width=3, dash="dash")
    )

    # Add launch annotation
    fig.add_annotation(
        x=datetime(2026, 2, 1),
        y=1.05,
        yref='paper',
        text='🚀 LAUNCH',
        showarrow=False,
        font=dict(size=16, color='red', family='Arial Black')
    )

    return fig


def create_postlaunch_gantt():
    """Create Post-Launch Roadmap Gantt Chart (Feb - Jul 2026)"""

    tasks = [
        # Q1 2026: Foundation
        dict(Task='Multi-Tenant Architecture', Start='2026-02-03', Finish='2026-02-23', Resource='Q1: Foundation', Type='foundation'),
        dict(Task='Team Collaboration Features', Start='2026-02-10', Finish='2026-03-02', Resource='Q1: Foundation', Type='foundation'),
        dict(Task='iOS Mobile App', Start='2026-02-03', Finish='2026-03-05', Resource='Q1: Foundation', Type='foundation'),
        dict(Task='Android Mobile App', Start='2026-02-10', Finish='2026-03-12', Resource='Q1: Foundation', Type='foundation'),
        dict(Task='Competitor Price Alerts', Start='2026-03-01', Finish='2026-03-13', Resource='Q1: Foundation', Type='automation'),
        dict(Task='Ranking Change Notifications', Start='2026-03-08', Finish='2026-03-21', Resource='Q1: Foundation', Type='automation'),

        # Q2 2026: Intelligence
        dict(Task='AI Recommendations Engine', Start='2026-05-01', Finish='2026-05-18', Resource='Q2: Intelligence', Type='analytics'),
        dict(Task='Priority Scoring System', Start='2026-05-12', Finish='2026-05-22', Resource='Q2: Intelligence', Type='analytics'),
        dict(Task='Opera PMS Integration', Start='2026-05-01', Finish='2026-05-21', Resource='Q2: Intelligence', Type='critical'),
        dict(Task='Mews PMS Integration', Start='2026-05-15', Finish='2026-05-30', Resource='Q2: Intelligence', Type='critical'),
        dict(Task='Booking.com API Integration', Start='2026-05-22', Finish='2026-06-06', Resource='Q2: Intelligence', Type='critical'),
        dict(Task='White-Label Reports', Start='2026-06-01', Finish='2026-06-16', Resource='Q2: Intelligence', Type='foundation'),
        dict(Task='Custom Branding System', Start='2026-06-10', Finish='2026-06-25', Resource='Q2: Intelligence', Type='foundation'),
        dict(Task='Predictive Analytics Model', Start='2026-06-15', Finish='2026-07-05', Resource='Q2: Intelligence', Type='analytics'),

        # Q3 2026: Advanced
        dict(Task='Automated Social Posting', Start='2026-08-01', Finish='2026-08-26', Resource='Q3: Advanced', Type='automation'),
        dict(Task='A/B Testing Platform', Start='2026-08-15', Finish='2026-09-04', Resource='Q3: Advanced', Type='analytics'),
        dict(Task='Internationalization (ES/FR)', Start='2026-09-01', Finish='2026-10-01', Resource='Q3: Advanced', Type='foundation'),
        dict(Task='Partner/Referral Program', Start='2026-09-15', Finish='2026-10-10', Resource='Q3: Advanced', Type='automation'),
    ]

    # Convert to DataFrame
    df = pd.DataFrame(tasks)

    # Create custom colors
    colors = []
    for task_type in df['Type']:
        colors.append(COLORS[task_type])

    # Create Gantt chart
    fig = ff.create_gantt(
        df,
        colors=colors,
        index_col='Resource',
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        showgrid_y=True,
        title='Hotel Grader: Post-Launch Roadmap (Feb - Oct 2026)',
        bar_width=0.4,
        height=700,
        width=1600
    )

    # Update layout
    fig.update_layout(
        xaxis_title='Timeline',
        yaxis_title='Features',
        font=dict(size=11),
        title_font=dict(size=20, color='#1F2937'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            tickformat='%b\n%Y',
            dtick='M1',  # 1 month
            gridcolor='#E5E7EB'
        ),
        yaxis=dict(gridcolor='#E5E7EB'),
        showlegend=False
    )

    # Add revenue milestone markers using shapes
    fig.add_shape(
        type="line",
        x0=datetime(2026, 5, 1),
        x1=datetime(2026, 5, 1),
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="green", width=2, dash="dash")
    )

    fig.add_shape(
        type="line",
        x0=datetime(2026, 8, 1),
        x1=datetime(2026, 8, 1),
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="green", width=2, dash="dash")
    )

    # Add milestone annotations
    fig.add_annotation(
        x=datetime(2026, 5, 1),
        y=1.05,
        yref='paper',
        text='💰 $5K MRR',
        showarrow=False,
        font=dict(size=14, color='green', family='Arial Black')
    )

    fig.add_annotation(
        x=datetime(2026, 8, 1),
        y=1.05,
        yref='paper',
        text='💰 $25K MRR',
        showarrow=False,
        font=dict(size=14, color='green', family='Arial Black')
    )

    return fig


def main():
    """Generate and save both charts"""

    print("🎨 Generating Pre-Launch Timeline Gantt Chart...")
    prelaunch_fig = create_prelaunch_gantt()

    # Export Pre-Launch chart (HTML only - browser can export to PNG/SVG)
    prelaunch_fig.write_html("timeline_prelaunch.html")
    print("✅ Pre-Launch chart saved: timeline_prelaunch.html")

    print("\n🎨 Generating Post-Launch Roadmap Gantt Chart...")
    postlaunch_fig = create_postlaunch_gantt()

    # Export Post-Launch chart (HTML only)
    postlaunch_fig.write_html("timeline_postlaunch.html")
    print("✅ Post-Launch chart saved: timeline_postlaunch.html")

    print("\n🎉 All charts generated successfully!")
    print("\nFiles created:")
    print("  📊 timeline_prelaunch.html (Interactive HTML)")
    print("  📊 timeline_postlaunch.html (Interactive HTML)")
    print("\n📝 To convert to PNG/SVG:")
    print("  1. Open the HTML files in your browser")
    print("  2. Click the camera icon in the toolbar (top-right)")
    print("  3. Download as PNG or SVG")
    print("  4. Or use browser screenshot tools for high-res images")

    # Create legend document
    legend_html = """
    <html>
    <head><title>Chart Legend</title></head>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Gantt Chart Legend</h2>
        <h3>Pre-Launch Timeline Colors:</h3>
        <ul>
            <li><span style="background-color: #EF4444; padding: 5px 10px; color: white;">Red</span> - Critical Path (must-have for launch)</li>
            <li><span style="background-color: #10B981; padding: 5px 10px; color: white;">Green</span> - Stretch Goals (optional if ahead of schedule)</li>
            <li><span style="background-color: #3B82F6; padding: 5px 10px; color: white;">Blue</span> - Foundation (database, auth, dashboard)</li>
            <li><span style="background-color: #8B5CF6; padding: 5px 10px; color: white;">Purple</span> - Analytics & Charts</li>
            <li><span style="background-color: #F59E0B; padding: 5px 10px; color: white;">Orange</span> - Automation & Billing</li>
            <li><span style="background-color: #6B7280; padding: 5px 10px; color: white;">Gray</span> - Launch Milestones</li>
        </ul>

        <h3>Key Milestones:</h3>
        <ul>
            <li>🚀 February 1, 2026 - PUBLIC LAUNCH</li>
            <li>💰 May 1, 2026 - $5K MRR Target</li>
            <li>💰 August 1, 2026 - $25K MRR Target</li>
        </ul>

        <h3>Timeline Breakdown:</h3>
        <ul>
            <li><strong>Weeks 1-2:</strong> Interactive scanning with live previews</li>
            <li><strong>Weeks 3-4:</strong> Enhanced map + 40-metric backend</li>
            <li><strong>Weeks 5-6:</strong> Database + Auth + Dashboard</li>
            <li><strong>Weeks 7-8:</strong> 40-metric frontend + Historical tracking</li>
            <li><strong>Weeks 9-10:</strong> Automation + Billing integration</li>
            <li><strong>Week 10.5:</strong> Final QA + Launch prep</li>
        </ul>
    </body>
    </html>
    """

    with open('chart_legend.html', 'w') as f:
        f.write(legend_html)
    print("  📋 chart_legend.html (Color legend and key milestones)")


if __name__ == '__main__':
    main()
