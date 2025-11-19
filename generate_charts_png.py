#!/usr/bin/env python3
"""
Generate PNG/SVG Gantt Charts using Matplotlib
Simpler alternative that doesn't require Chrome
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
import matplotlib.dates as mdates

# Color scheme
COLORS = {
    'critical': '#EF4444',      # Red - Critical path
    'stretch': '#10B981',       # Green - Stretch goals
    'foundation': '#3B82F6',    # Blue - Foundation
    'analytics': '#8B5CF6',     # Purple - Analytics
    'automation': '#F59E0B',    # Orange - Automation
    'milestone': '#6B7280'      # Gray - Milestones
}

def create_prelaunch_gantt_png():
    """Create Pre-Launch Timeline Gantt Chart as PNG"""

    # Define tasks
    tasks = [
        # Phase 0: Lead Generation
        ('Interactive Scanning: Images', '2025-11-19', 8, 'critical'),
        ('Interactive Scanning: Reviews/Rankings', '2025-11-23', 6, 'critical'),
        ('Enhanced Competitor Map', '2025-12-03', 5, 'critical'),
        ('Competitor Ranking Summary', '2025-12-06', 3, 'critical'),
        ('40-Metric Backend (AI Prompt)', '2025-12-03', 5, 'critical'),
        ('40-Metric Backend (OTA Scraping)', '2025-12-08', 8, 'critical'),

        # Stretch Goals
        ('🎁 Social Sharing Feature', '2025-12-10', 3, 'stretch'),
        ('🎁 Live Chat Widget', '2025-12-13', 5, 'stretch'),
        ('🎁 Voice-Over Narration', '2025-12-13', 4, 'stretch'),

        # Phase 1: Foundation
        ('Database Schema & Setup', '2025-12-17', 5, 'foundation'),
        ('JWT Authentication', '2025-12-20', 6, 'foundation'),
        ('User Registration/Login', '2025-12-24', 4, 'foundation'),
        ('Main Dashboard UI', '2025-12-26', 7, 'foundation'),
        ('Multi-Property Support', '2025-12-30', 5, 'foundation'),

        # Analytics
        ('40-Metric Frontend Components', '2025-12-31', 10, 'analytics'),
        ('Chart Library Integration', '2026-01-05', 6, 'analytics'),
        ('Historical Data Storage', '2026-01-08', 5, 'analytics'),
        ('Progress Tracking UI', '2026-01-10', 5, 'analytics'),

        # Automation
        ('Automated Analysis Engine', '2026-01-14', 8, 'automation'),
        ('Email Alerts & Notifications', '2026-01-18', 4, 'automation'),
        ('Stripe Integration', '2026-01-20', 7, 'automation'),
        ('Feature Management Interface', '2026-01-24', 4, 'automation'),

        # Launch
        ('🚀 Final QA & Testing', '2026-01-28', 2, 'milestone'),
        ('🚀 Performance Optimization', '2026-01-29', 2, 'milestone'),
        ('🚀 Documentation', '2026-01-30', 2, 'milestone'),
    ]

    # Create figure
    fig, ax = plt.subplots(figsize=(18, 10))

    # Process tasks
    y_pos = 0
    y_labels = []
    y_ticks = []

    for task_name, start_date, duration, task_type in tasks:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = start + timedelta(days=duration)

        # Draw bar
        ax.barh(y_pos, (end - start).days, left=start, height=0.6,
                color=COLORS[task_type], alpha=0.9, edgecolor='white', linewidth=1)

        y_labels.append(task_name)
        y_ticks.append(y_pos)
        y_pos += 1

    # Add launch date line
    launch_date = datetime(2026, 2, 1)
    ax.axvline(launch_date, color='red', linestyle='--', linewidth=3, alpha=0.7)
    ax.text(launch_date, len(tasks) + 0.5, '🚀 LAUNCH\nFeb 1, 2026',
            ha='center', va='bottom', fontsize=14, color='red', fontweight='bold')

    # Format x-axis (dates)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d\n%Y'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.xticks(rotation=0, ha='center')

    # Format y-axis (tasks)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, fontsize=9)
    ax.invert_yaxis()  # Top to bottom

    # Labels and title
    ax.set_xlabel('Timeline', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tasks', fontsize=12, fontweight='bold')
    ax.set_title('Hotel Grader: Pre-Launch Timeline (Nov 19, 2025 → Feb 1, 2026)',
                 fontsize=16, fontweight='bold', pad=20)

    # Grid
    ax.grid(True, axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    # Legend
    legend_elements = [
        mpatches.Patch(color=COLORS['critical'], label='Critical Path'),
        mpatches.Patch(color=COLORS['stretch'], label='Stretch Goals'),
        mpatches.Patch(color=COLORS['foundation'], label='SaaS Foundation'),
        mpatches.Patch(color=COLORS['analytics'], label='Analytics & Charts'),
        mpatches.Patch(color=COLORS['automation'], label='Automation & Billing'),
        mpatches.Patch(color=COLORS['milestone'], label='Launch Milestones'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

    # Add phase labels
    ax.text(datetime(2025, 12, 1), -1, 'Phase 0: Interactive Lead Gen',
            ha='center', va='bottom', fontsize=12, color='#EF4444', fontweight='bold')
    ax.text(datetime(2026, 1, 10), -1, 'Phase 1: SaaS Foundation',
            ha='center', va='bottom', fontsize=12, color='#3B82F6', fontweight='bold')

    plt.tight_layout()

    return fig


def create_postlaunch_gantt_png():
    """Create Post-Launch Roadmap Gantt Chart as PNG"""

    # Define tasks
    tasks = [
        # Q1 2026
        ('Multi-Tenant Architecture', '2026-02-03', 20, 'foundation'),
        ('Team Collaboration Features', '2026-02-10', 20, 'foundation'),
        ('iOS Mobile App', '2026-02-03', 30, 'foundation'),
        ('Android Mobile App', '2026-02-10', 30, 'foundation'),
        ('Competitor Price Alerts', '2026-03-01', 12, 'automation'),
        ('Ranking Change Notifications', '2026-03-08', 13, 'automation'),

        # Q2 2026
        ('AI Recommendations Engine', '2026-05-01', 17, 'analytics'),
        ('Priority Scoring System', '2026-05-12', 10, 'analytics'),
        ('Opera PMS Integration', '2026-05-01', 20, 'critical'),
        ('Mews PMS Integration', '2026-05-15', 15, 'critical'),
        ('Booking.com API Integration', '2026-05-22', 15, 'critical'),
        ('White-Label Reports', '2026-06-01', 15, 'foundation'),
        ('Custom Branding System', '2026-06-10', 15, 'foundation'),
        ('Predictive Analytics Model', '2026-06-15', 20, 'analytics'),

        # Q3 2026
        ('Automated Social Posting', '2026-08-01', 25, 'automation'),
        ('A/B Testing Platform', '2026-08-15', 20, 'analytics'),
        ('Internationalization (ES/FR)', '2026-09-01', 30, 'foundation'),
        ('Partner/Referral Program', '2026-09-15', 25, 'automation'),
    ]

    # Create figure
    fig, ax = plt.subplots(figsize=(18, 9))

    # Process tasks
    y_pos = 0
    y_labels = []
    y_ticks = []

    for task_name, start_date, duration, task_type in tasks:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = start + timedelta(days=duration)

        # Draw bar
        ax.barh(y_pos, (end - start).days, left=start, height=0.6,
                color=COLORS[task_type], alpha=0.9, edgecolor='white', linewidth=1)

        y_labels.append(task_name)
        y_ticks.append(y_pos)
        y_pos += 1

    # Add revenue milestone lines
    milestone_may = datetime(2026, 5, 1)
    milestone_aug = datetime(2026, 8, 1)

    ax.axvline(milestone_may, color='green', linestyle='--', linewidth=2, alpha=0.7)
    ax.text(milestone_may, len(tasks) + 0.5, '💰 $5K MRR',
            ha='center', va='bottom', fontsize=12, color='green', fontweight='bold')

    ax.axvline(milestone_aug, color='green', linestyle='--', linewidth=2, alpha=0.7)
    ax.text(milestone_aug, len(tasks) + 0.5, '💰 $25K MRR',
            ha='center', va='bottom', fontsize=12, color='green', fontweight='bold')

    # Format x-axis (dates)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=0, ha='center')

    # Format y-axis (tasks)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, fontsize=9)
    ax.invert_yaxis()  # Top to bottom

    # Labels and title
    ax.set_xlabel('Timeline', fontsize=12, fontweight='bold')
    ax.set_ylabel('Features', fontsize=12, fontweight='bold')
    ax.set_title('Hotel Grader: Post-Launch Roadmap (Feb - Oct 2026)',
                 fontsize=16, fontweight='bold', pad=20)

    # Grid
    ax.grid(True, axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    # Legend
    legend_elements = [
        mpatches.Patch(color=COLORS['critical'], label='Integrations'),
        mpatches.Patch(color=COLORS['foundation'], label='Foundation'),
        mpatches.Patch(color=COLORS['analytics'], label='Intelligence'),
        mpatches.Patch(color=COLORS['automation'], label='Automation'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

    # Add quarter labels
    ax.text(datetime(2026, 3, 15), -1, 'Q1: Foundation & Mobile',
            ha='center', va='bottom', fontsize=12, color='#3B82F6', fontweight='bold')
    ax.text(datetime(2026, 6, 1), -1, 'Q2: Intelligence & Integrations',
            ha='center', va='bottom', fontsize=12, color='#8B5CF6', fontweight='bold')
    ax.text(datetime(2026, 9, 1), -1, 'Q3: Advanced Features',
            ha='center', va='bottom', fontsize=12, color='#F59E0B', fontweight='bold')

    plt.tight_layout()

    return fig


def main():
    """Generate and save both charts as PNG and SVG"""

    print("🎨 Generating Pre-Launch Timeline Gantt Chart (PNG/SVG)...")
    prelaunch_fig = create_prelaunch_gantt_png()

    # Export Pre-Launch chart
    prelaunch_fig.savefig('timeline_prelaunch.png', dpi=300, bbox_inches='tight', facecolor='white')
    prelaunch_fig.savefig('timeline_prelaunch.svg', format='svg', bbox_inches='tight', facecolor='white')
    print("✅ Pre-Launch chart saved: timeline_prelaunch.png, .svg")
    plt.close(prelaunch_fig)

    print("\n🎨 Generating Post-Launch Roadmap Gantt Chart (PNG/SVG)...")
    postlaunch_fig = create_postlaunch_gantt_png()

    # Export Post-Launch chart
    postlaunch_fig.savefig('timeline_postlaunch.png', dpi=300, bbox_inches='tight', facecolor='white')
    postlaunch_fig.savefig('timeline_postlaunch.svg', format='svg', bbox_inches='tight', facecolor='white')
    print("✅ Post-Launch chart saved: timeline_postlaunch.png, .svg")
    plt.close(postlaunch_fig)

    print("\n🎉 All PNG/SVG charts generated successfully!")
    print("\nFiles created:")
    print("  📊 timeline_prelaunch.png (High-res PNG, 300 DPI)")
    print("  📊 timeline_prelaunch.svg (Vector SVG)")
    print("  📊 timeline_postlaunch.png (High-res PNG, 300 DPI)")
    print("  📊 timeline_postlaunch.svg (Vector SVG)")
    print("\n💡 These charts are print-ready and perfect for presentations!")


if __name__ == '__main__':
    main()
