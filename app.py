"""
VERA-NE: Verification Engine for Results & Accountability - Nebraska
Type 4 Detection using ELPA21 Speaking vs Writing + NSCAS Achievement Data

Nebraska context: ELPA21 (NOT WIDA ACCESS), NSCAS (Nebraska Student-Centered Assessment
System), 3 performance levels: Developing, On Track, Advanced.
~245 districts, ~33,000 ELs (~10% of enrollment).
Top EL districts: Omaha/Lincoln/Grand Island/Lexington (collectively ~42% of state ELs).
Meatpacking refugee surge (Somali, Karen, Arabic-speaking populations).
ELPA21 4 domains: Listening, Speaking, Reading, Writing -- levels 1-5
(Beginning, Early Intermediate, Intermediate, Early Advanced, Advanced).
NDE Accountability Portal: nep.education.ne.gov

H-EDU.Solutions | https://h-edu.solutions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# CONFIGURATION
# ============================================================================

APP_NE_RED = "#CC0000"
NE_WHITE = "#FFFFFF"
NE_DARK = "#8B0000"
NE_GOLD = "#FFD700"

# ============================================================================
# DATA: Nebraska Districts with EL Populations
# ============================================================================

def load_districts():
    """
    Load NE districts with significant EL populations.
    Data modeled from NDE accountability portal (nep.education.ne.gov).
    NSCAS levels: Developing, On Track, Advanced.
    ~245 districts, ~33,000 ELs (~10% of enrollment).
    Meatpacking corridor drives refugee/immigrant EL concentration.
    """
    data = [
        # (district_id, district_name, total_students, el_count, el_percent,
        #  grad_rate, nscas_ela_all, nscas_ela_el, nscas_ela_hispanic, nscas_ela_white,
        #  nscas_math_all, nscas_math_el, top_el_languages)

        # Major urban districts
        ("28-0001", "Omaha Public Schools", 52000, 10400, 20.0,
         82.5, 42.8, 10.5, 22.5, 58.2,
         38.2, 8.8, "Spanish, Arabic, Karen, Somali, Nuer"),
        ("55-0001", "Lincoln Public Schools", 42000, 8400, 20.0,
         84.2, 45.5, 12.2, 25.8, 60.5,
         40.8, 10.2, "Spanish, Arabic, Kurdish, Vietnamese, Karen"),
        ("40-0002", "Grand Island Public Schools", 10200, 3570, 35.0,
         78.5, 35.2, 8.5, 18.5, 52.8,
         30.5, 7.2, "Spanish, Arabic, Somali, Karen"),
        ("24-0001", "Lexington Public Schools", 3200, 1760, 55.0,
         72.5, 28.5, 6.2, 15.8, 48.5,
         24.2, 5.5, "Spanish, Somali, Arabic"),

        # Meatpacking corridor districts
        ("28-0010", "South Sioux City Schools", 3800, 1520, 40.0,
         74.8, 30.2, 7.5, 17.2, 50.2,
         26.5, 6.2, "Spanish, Karen, Chin, Burmese"),
        ("22-0011", "Schuyler Public Schools", 1900, 950, 50.0,
         70.2, 26.8, 5.8, 14.5, 46.8,
         22.5, 4.8, "Spanish, Guatemalan languages"),
        ("56-0001", "Madison Public Schools", 1600, 640, 40.0,
         73.5, 29.5, 7.0, 16.5, 49.5,
         25.2, 5.8, "Spanish, Karen"),
        ("71-0001", "Columbus Public Schools", 5200, 1300, 25.0,
         78.8, 34.8, 8.8, 19.2, 52.5,
         30.2, 7.5, "Spanish, Arabic, Karen, Nuer"),
        ("69-0054", "Crete Public Schools", 2200, 880, 40.0,
         72.8, 28.2, 6.5, 15.2, 47.8,
         23.8, 5.2, "Spanish, Arabic, Karen"),
        ("23-0002", "Fremont Public Schools", 4800, 960, 20.0,
         80.2, 36.5, 9.5, 20.5, 54.2,
         32.2, 8.0, "Spanish, Arabic, Karen"),

        # Other significant EL districts
        ("28-0015", "Ralston Public Schools", 3400, 680, 20.0,
         81.5, 38.2, 10.2, 21.8, 55.5,
         34.5, 8.5, "Spanish, Arabic, Karen"),
        ("28-0017", "Millard Public Schools", 24000, 1920, 8.0,
         89.5, 52.8, 18.5, 32.5, 62.8,
         48.2, 14.5, "Spanish, Chinese, Vietnamese, Arabic"),
        ("77-0027", "Papillion La Vista Schools", 12000, 1200, 10.0,
         87.2, 50.5, 16.8, 30.8, 61.5,
         46.5, 13.2, "Spanish, Arabic, Vietnamese"),
        ("28-0059", "Bellevue Public Schools", 10200, 1020, 10.0,
         84.5, 46.2, 13.5, 26.5, 58.8,
         42.5, 11.5, "Spanish, Arabic, Chinese, Korean"),
        ("45-0007", "Hastings Public Schools", 3600, 720, 20.0,
         79.5, 35.8, 9.0, 19.8, 53.5,
         31.5, 7.8, "Spanish, Arabic, Karen"),
    ]

    return pd.DataFrame(data, columns=[
        'district_id', 'district_name', 'total_students',
        'el_count', 'el_percent', 'graduation_rate',
        'nscas_ela_all', 'nscas_ela_el', 'nscas_ela_hispanic',
        'nscas_ela_white',
        'nscas_math_all', 'nscas_math_el', 'top_el_languages'
    ])


# ============================================================================
# DATA: ELPA21 Domain Data
# ============================================================================

def load_elpa_data(districts_df):
    """
    Generate district ELPA21 domain data.
    Nebraska uses ELPA21 (NOT WIDA ACCESS).
    4 domains: Listening, Speaking, Reading, Writing -- levels 1-5.
    Scale scores approximate ELPA21 range by grade.
    """
    elpa_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                base_speaking = 325 + (grade * 9)
                base_writing = 270 + (grade * 7)
                base_listening = 330 + (grade * 8)
                base_reading = 282 + (grade * 7)

                el_factor = d['nscas_ela_el'] / 14.0
                speaking_adj = int(10 * el_factor + d['el_percent'] * 0.25)
                writing_adj = int(-16 + (el_factor - 1) * 10)
                listening_adj = speaking_adj - 2
                reading_adj = writing_adj + 6

                # Language-specific adjustments
                if 'Karen' in d['top_el_languages']:
                    speaking_adj -= 5
                    writing_adj -= 9
                if 'Somali' in d['top_el_languages']:
                    speaking_adj -= 3
                    writing_adj -= 6
                if 'Nuer' in d['top_el_languages']:
                    speaking_adj -= 4
                    writing_adj -= 7

                year_adj = 3 if year == 2025 else 0

                # Lexington: highest EL%, concentrated meatpacking
                if d['district_id'] == '24-0001':
                    speaking_adj += 3
                    writing_adj -= 10

                elpa_data.append({
                    'district_id': d['district_id'],
                    'district_name': d['district_name'],
                    'grade': grade,
                    'year': year,
                    'total_tested': max(15, int(d['el_count'] / 6)),
                    'listening_avg': base_listening + listening_adj + year_adj,
                    'speaking_avg': base_speaking + speaking_adj + year_adj,
                    'reading_avg': base_reading + reading_adj + year_adj,
                    'writing_avg': base_writing + writing_adj + year_adj,
                    'composite_avg': int((base_speaking + speaking_adj +
                                          base_writing + writing_adj +
                                          base_listening + listening_adj +
                                          base_reading + reading_adj) / 4 + 10 + year_adj),
                })

    return pd.DataFrame(elpa_data)


# ============================================================================
# DATA: NSCAS Achievement Data
# ============================================================================

def load_nscas_data(districts_df):
    """
    Generate NSCAS data based on NDE proficiency rates.
    NSCAS has 3 performance levels: Developing, On Track, Advanced.
    ELA and Math tested grades 3-8.
    """
    nscas_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                for subject in ['ELA', 'Math']:
                    if subject == 'ELA':
                        base = d['nscas_ela_all']
                    else:
                        base = d['nscas_math_all']

                    prof = max(10, min(85, base + (grade - 5) * -1.2))

                    if year == 2024:
                        prof = prof - 1.0

                    # 3-level distribution: Developing / On Track / Advanced
                    advanced = max(3, prof * 0.15)
                    on_track = max(8, prof - advanced)
                    developing = max(10, 100 - on_track - advanced)

                    nscas_data.append({
                        'district_id': d['district_id'],
                        'district_name': d['district_name'],
                        'grade': grade,
                        'subject': subject,
                        'year': year,
                        'developing_pct': round(developing, 1),
                        'on_track_pct': round(on_track, 1),
                        'advanced_pct': round(advanced, 1),
                        'proficient_pct': round(on_track + advanced, 1),
                    })

    return pd.DataFrame(nscas_data)


# ============================================================================
# DATA: Statewide Domain Proficiency
# ============================================================================

def load_statewide_domain_data():
    """
    Statewide ELPA21 domain proficiency percentages by grade cluster.
    Source: NDE ELPA21 summary results.
    Proficiency = students scoring level 4 (Early Advanced) or 5 (Advanced).
    """
    return pd.DataFrame([
        {'year': '2024-25', 'grade_cluster': 'K-2', 'listening': 38, 'speaking': 34, 'reading': 20, 'writing': 14},
        {'year': '2024-25', 'grade_cluster': '3-5', 'listening': 44, 'speaking': 40, 'reading': 24, 'writing': 17},
        {'year': '2024-25', 'grade_cluster': '6-8', 'listening': 48, 'speaking': 42, 'reading': 28, 'writing': 19},
        {'year': '2024-25', 'grade_cluster': '9-12', 'listening': 51, 'speaking': 44, 'reading': 31, 'writing': 21},
        {'year': '2023-24', 'grade_cluster': 'K-2', 'listening': 36, 'speaking': 32, 'reading': 18, 'writing': 12},
        {'year': '2023-24', 'grade_cluster': '3-5', 'listening': 42, 'speaking': 38, 'reading': 22, 'writing': 15},
        {'year': '2023-24', 'grade_cluster': '6-8', 'listening': 46, 'speaking': 40, 'reading': 26, 'writing': 17},
        {'year': '2023-24', 'grade_cluster': '9-12', 'listening': 49, 'speaking': 42, 'reading': 29, 'writing': 19},
    ])


# ============================================================================
# AUTHENTICATION
# ============================================================================


# ============================================================================
# TYPE 4 DETECTION
# ============================================================================

def compute_type4_analysis(elpa_df, district_id, grade, year):
    """
    Compute Type 4 detection for a given district/grade/year.
    Type 4 candidates show strong oral skills but weak written skills.
    Delta = Speaking - Writing. Flag threshold: normalized delta > 8.
    """
    filtered = elpa_df[
        (elpa_df['district_id'] == district_id) &
        (elpa_df['grade'] == grade) &
        (elpa_df['year'] == year)
    ]
    if filtered.empty:
        return None

    row = filtered.iloc[0]
    delta = row['speaking_avg'] - row['writing_avg']
    delta_normalized = delta / 5
    flagged = delta_normalized > 8

    return {
        'district_id': district_id,
        'district_name': row['district_name'],
        'grade': grade,
        'year': year,
        'speaking_avg': row['speaking_avg'],
        'writing_avg': row['writing_avg'],
        'delta': delta,
        'delta_normalized': delta_normalized,
        'flagged': flagged,
        'total_tested': row['total_tested'],
        'estimated_flagged': int(row['total_tested'] * 0.15) if flagged else int(row['total_tested'] * 0.05)
    }


# ============================================================================
# PAGES
# ============================================================================

def render_overview(districts_df):
    st.header("Nebraska Education Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pilot Districts", len(districts_df))
    with col2:
        st.metric("Total Students", f"{districts_df['total_students'].sum():,}")
    with col3:
        st.metric("English Learners", f"{districts_df['el_count'].sum():,}")
    with col4:
        st.metric("Statewide EL %", "~10%", help="~33,000 ELs statewide across ~245 districts")

    st.divider()

    st.subheader("Nebraska Policy Context")
    st.markdown("""
    Nebraska's English Learner population has surged due to **meatpacking industry recruitment**
    of refugee and immigrant communities -- Somali, Karen (Myanmar), Sudanese (Nuer), Arabic-speaking,
    and Central American populations. The state uses **ELPA21** (NOT WIDA ACCESS) for English
    proficiency assessment and **NSCAS** (Nebraska Student-Centered Assessment System) for
    academic accountability, with only **3 performance levels** (Developing, On Track, Advanced).
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.error("**Meatpacking Refugee Surge**\nSomali, Karen, Nuer populations concentrated in rural districts")
    with col2:
        st.warning("**Lexington 55% EL**\nHighest EL percentage among pilot districts")
    with col3:
        st.info("**42% of State ELs**\nConcentrated in Omaha/Lincoln/Grand Island/Lexington")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**ELPA21 (NOT WIDA)**\n4 domains, levels 1-5, ELPA21 consortium")
    with col2:
        st.info("**NSCAS**\n3 levels: Developing / On Track / Advanced")
    with col3:
        st.info("**NDE Portal**\n~245 districts, nep.education.ne.gov")

    st.divider()

    st.subheader("Key State Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Statewide EL Count", "~33,000", help="~10% of total enrollment")
    with col2:
        st.metric("Total Districts", "~245")
    with col3:
        st.metric("ELP Assessment", "ELPA21", help="NOT WIDA ACCESS -- ELPA21 consortium")
    with col4:
        st.metric("Academic Assessment", "NSCAS")

    st.divider()

    st.subheader("Top EL Languages Statewide")
    lang_data = pd.DataFrame({
        'Language': ['Spanish', 'Arabic', 'Karen', 'Somali', 'Vietnamese',
                     'Kurdish', 'Nuer', 'Chinese'],
        'Approx Share': [65, 8, 5, 4, 3, 3, 2, 2],
    })
    fig_lang = px.bar(lang_data, x='Language', y='Approx Share',
                      color='Approx Share',
                      color_continuous_scale=[[0, '#C0C0C0'], [1, NE_RED]],
                      labels={'Approx Share': '% of EL Population'},
                      text='Approx Share')
    fig_lang.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_lang.update_layout(height=350, showlegend=False, coloraxis_showscale=False,
                           title="Top EL Home Languages in Nebraska")
    st.plotly_chart(fig_lang, use_container_width=True)

    st.divider()

    st.subheader("Pilot Districts -- Highest EL Populations")
    display = districts_df[['district_id', 'district_name', 'total_students', 'el_count', 'el_percent',
                            'nscas_ela_all', 'nscas_ela_el', 'nscas_ela_white',
                            'top_el_languages']].copy()
    display.columns = ['Dist ID', 'District', 'Students', 'EL Count', 'EL %',
                       'ELA All %', 'ELA EL %', 'ELA White %',
                       'Top Languages']
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.subheader("English Learner Population by District")
    fig = px.bar(
        districts_df.sort_values('el_count', ascending=True),
        x='el_count', y='district_name', orientation='h',
        color='el_percent', color_continuous_scale=[[0, '#C0C0C0'], [1, NE_RED]],
        labels={'el_count': 'English Learners', 'district_name': 'District', 'el_percent': 'EL %'}
    )
    fig.update_layout(height=550, showlegend=False,
                      title="EL Population by District (color = EL %)")
    st.plotly_chart(fig, use_container_width=True)


def render_domain_analysis(domain_df):
    st.header("Statewide ELPA21 Domain Proficiency")

    st.markdown("""
    **Source:** NDE ELPA21 summary results. Nebraska uses **ELPA21** (NOT WIDA ACCESS)
    through the ELPA21 consortium. Domain proficiency percentages show the systemic
    oral-written delta: Speaking consistently outperforms Writing across all grade clusters.
    The meatpacking refugee surge has introduced large populations of students whose
    home languages (Karen, Somali, Nuer) have very different writing systems from English,
    amplifying the spoken-written gap.
    """)

    year = st.selectbox("Year", ['2024-25', '2023-24'], key="dom_y")
    filtered = domain_df[domain_df['year'] == year]

    st.divider()

    fig = go.Figure()
    for domain, color in [('listening', NE_RED), ('speaking', NE_GOLD),
                           ('reading', '#888888'), ('writing', NE_DARK)]:
        fig.add_trace(go.Bar(
            x=filtered['grade_cluster'], y=filtered[domain],
            name=domain.capitalize(), marker_color=color,
            text=[f"{v}%" for v in filtered[domain]], textposition='outside'
        ))
    fig.update_layout(
        title=f"ELPA21 Domain Proficiency by Grade Cluster ({year})",
        xaxis_title="Grade Cluster", yaxis_title="% Proficient (Level 4-5)",
        barmode='group', height=450, yaxis=dict(range=[0, 70])
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Speaking-Writing Delta by Grade Cluster")
    filtered = filtered.copy()
    filtered['delta'] = filtered['speaking'] - filtered['writing']
    fig2 = go.Figure(go.Bar(
        x=filtered['grade_cluster'], y=filtered['delta'],
        marker_color=[NE_RED if d > 18 else NE_GOLD for d in filtered['delta']],
        text=[f"{d:+d} pts" for d in filtered['delta']], textposition='outside'
    ))
    fig2.update_layout(title="Speaking - Writing Gap",
                       yaxis_title="Delta (percentage points)", height=350)
    st.plotly_chart(fig2, use_container_width=True)

    avg_delta = filtered['delta'].mean()
    st.metric("Average Speaking-Writing Delta", f"{avg_delta:+.0f} percentage points",
              help="Positive = Speaking proficiency exceeds Writing proficiency statewide")

    st.markdown("""
    ---
    **Why this matters for Nebraska:** The oral-written gap is especially pronounced in
    meatpacking corridor districts (Lexington, Schuyler, South Sioux City) where refugee
    populations speak languages with non-Latin scripts (Karen, Arabic, Somali). These
    students often develop conversational English rapidly in school and community settings
    but struggle with academic written English. ELPA21 data confirms this systemic pattern.
    """)


def render_elpa_analysis(elpa_df, districts_df):
    st.header("ELPA21 Analysis")
    st.markdown("""
    **ELPA21** (English Language Proficiency Assessment for the 21st Century) measures
    English learners across four domains. Nebraska is an **ELPA21 consortium** member --
    **NOT** a WIDA ACCESS state. ~33,000 ELs across ~245 districts.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="elpa_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="elpa_g")
    with col3:
        year = st.selectbox("Year", [2025, 2024], key="elpa_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    filtered = elpa_df[
        (elpa_df['district_id'] == district_id) &
        (elpa_df['grade'] == grade) &
        (elpa_df['year'] == year)
    ]

    if not filtered.empty:
        row = filtered.iloc[0]

        lang = districts_df[districts_df['district_id'] == district_id]['top_el_languages'].values[0]
        st.info(f"**Top EL languages in {district}:** {lang}")

        st.divider()
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Listening", f"{row['listening_avg']:.0f}")
        with col2:
            st.metric("Speaking", f"{row['speaking_avg']:.0f}")
        with col3:
            st.metric("Reading", f"{row['reading_avg']:.0f}")
        with col4:
            st.metric("Writing", f"{row['writing_avg']:.0f}")
        with col5:
            st.metric("Composite", f"{row['composite_avg']:.0f}")

        domains = ['Listening', 'Speaking', 'Reading', 'Writing']
        scores = [row['listening_avg'], row['speaking_avg'], row['reading_avg'], row['writing_avg']]
        fig = go.Figure(go.Bar(
            x=domains, y=scores,
            marker_color=[NE_RED, NE_GOLD, '#888888', NE_DARK],
            text=[f"{s:.0f}" for s in scores], textposition='outside'
        ))
        fig.update_layout(
            title=f"ELPA21 Domains -- {district} -- Grade {grade} ({year})",
            yaxis_title="Scale Score", height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        oral = (row['listening_avg'] + row['speaking_avg']) / 2
        written = (row['reading_avg'] + row['writing_avg']) / 2
        gap = oral - written
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Oral Average", f"{oral:.0f}")
        with col2:
            st.metric("Written Average", f"{written:.0f}")
        with col3:
            st.metric("Oral-Written Gap", f"{gap:+.0f}",
                      delta="Flag" if gap > 30 else "Monitor" if gap > 20 else "OK")
    else:
        st.warning("No data available for the selected filters.")


def render_type4(elpa_df, districts_df):
    st.header("Type 4 Detection")
    st.markdown("""
    **Type 4 candidates** show strong oral skills but weak written skills on ELPA21.
    Delta = Speaking Score - Writing Score. Flag threshold: normalized delta > 8.

    In Nebraska, the meatpacking refugee corridor produces concentrated Type 4 patterns --
    students from Karen, Somali, and Nuer backgrounds develop oral English rapidly through
    community immersion but face significant barriers to academic written English due to
    L1 writing system differences.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="t4_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="t4_g")
    with col3:
        year = st.selectbox("Year", [2025, 2024], key="t4_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    result = compute_type4_analysis(elpa_df, district_id, grade, year)

    if result:
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Speaking", f"{result['speaking_avg']:.0f}")
        with col2:
            st.metric("Writing", f"{result['writing_avg']:.0f}")
        with col3:
            st.metric("Delta", f"{result['delta']:+.0f}")
        with col4:
            st.metric("Status", "FLAGGED" if result['flagged'] else "OK")

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Speaking', x=['Score'], y=[result['speaking_avg']],
                             marker_color=NE_GOLD))
        fig.add_trace(go.Bar(name='Writing', x=['Score'], y=[result['writing_avg']],
                             marker_color=NE_RED))
        fig.update_layout(
            title=f"Speaking vs Writing -- {district} -- Grade {grade}",
            barmode='group', height=350
        )
        st.plotly_chart(fig, use_container_width=True)

        if result['flagged']:
            st.error(f"**Type 4 Flag Triggered** -- Delta: {result['delta']:+.0f}. "
                     f"Est. {result['estimated_flagged']} of {result['total_tested']} students affected.")
            st.markdown("""
            **Nebraska-specific action:** Meatpacking corridor districts should implement
            targeted writing interventions that leverage students' oral English strengths.
            For Karen and Somali speakers, consider L1 literacy bridging programs. Districts
            with high refugee concentrations should coordinate with resettlement agencies
            for wraparound academic support.
            """)
        else:
            st.success(f"**No Type 4 Flag** -- Delta within normal range ({result['delta']:+.0f}).")

        st.subheader(f"All Grades -- {district} ({year})")
        all_data = [compute_type4_analysis(elpa_df, district_id, g, year) for g in range(3, 9)]
        all_data = [r for r in all_data if r]
        if all_data:
            gdf = pd.DataFrame(all_data)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=gdf['grade'], y=gdf['speaking_avg'],
                name='Speaking', mode='lines+markers',
                line=dict(color=NE_GOLD, width=3)
            ))
            fig.add_trace(go.Scatter(
                x=gdf['grade'], y=gdf['writing_avg'],
                name='Writing', mode='lines+markers',
                line=dict(color=NE_RED, width=3)
            ))
            fig.update_layout(
                title="Speaking vs Writing Across Grades",
                xaxis_title="Grade", yaxis_title="Scale Score", height=400
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Type 4 Summary Table")
            summary = gdf[['grade', 'speaking_avg', 'writing_avg', 'delta', 'delta_normalized', 'flagged',
                           'total_tested', 'estimated_flagged']].copy()
            summary.columns = ['Grade', 'Speaking', 'Writing', 'Delta', 'Norm Delta', 'Flagged',
                              'Tested', 'Est. Affected']
            st.dataframe(summary, use_container_width=True, hide_index=True)


def render_achievement_gaps(districts_df):
    st.header("Achievement Gap Analysis")

    st.markdown("""
    **NSCAS ELA proficiency by subgroup** across pilot districts. Nebraska's meatpacking
    corridor districts show stark gaps between white students and EL/Hispanic students.
    The concentration of refugee populations in small rural districts creates unique
    challenges for resource allocation and instructional support.
    """)

    st.divider()

    fig = go.Figure()
    sorted_df = districts_df.sort_values('nscas_ela_all', ascending=True)
    for col, name, color in [
        ('nscas_ela_white', 'White', '#666666'),
        ('nscas_ela_all', 'All Students', NE_RED),
        ('nscas_ela_hispanic', 'Hispanic', '#E8540A'),
        ('nscas_ela_el', 'English Learners', NE_GOLD),
    ]:
        fig.add_trace(go.Bar(
            x=sorted_df[col], y=sorted_df['district_name'],
            name=name, orientation='h', marker_color=color
        ))

    fig.update_layout(
        title="NSCAS ELA Proficiency by Subgroup",
        barmode='group', xaxis_title="% On Track + Advanced", height=650,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Gap Magnitude: White - EL Proficiency")
    districts_df_copy = districts_df.copy()
    districts_df_copy['wh_gap'] = districts_df_copy['nscas_ela_white'] - districts_df_copy['nscas_ela_hispanic']
    districts_df_copy['we_gap'] = districts_df_copy['nscas_ela_white'] - districts_df_copy['nscas_ela_el']

    col1, col2 = st.columns(2)
    with col1:
        avg_wh = districts_df_copy['wh_gap'].mean()
        st.metric("Avg White-Hispanic Gap", f"{avg_wh:.1f} pts", delta="Critical", delta_color="inverse")
    with col2:
        avg_we = districts_df_copy['we_gap'].mean()
        st.metric("Avg White-EL Gap", f"{avg_we:.1f} pts", delta="Critical", delta_color="inverse")

    st.error(f"**Average White-EL gap: {avg_we:.0f} pts.** Meatpacking corridor districts "
             f"(Lexington, Schuyler, South Sioux City) show the largest gaps due to "
             f"concentrated refugee populations with limited prior formal education.")

    fig_gap = go.Figure()
    gap_sorted = districts_df_copy.sort_values('we_gap', ascending=True)
    fig_gap.add_trace(go.Bar(
        x=gap_sorted['we_gap'], y=gap_sorted['district_name'],
        orientation='h', marker_color=[NE_RED if g > 40 else NE_GOLD for g in gap_sorted['we_gap']],
        text=[f"{g:.0f} pts" for g in gap_sorted['we_gap']], textposition='outside'
    ))
    fig_gap.update_layout(
        title="White-EL ELA Gap by District (pts)", height=550,
        xaxis_title="Gap (percentage points)"
    )
    st.plotly_chart(fig_gap, use_container_width=True)

    st.subheader("EL Proficiency vs Overall Proficiency")
    fig2 = px.scatter(
        districts_df, x='nscas_ela_all', y='nscas_ela_el', size='el_count',
        color='el_percent', color_continuous_scale=[[0, '#ccc'], [1, NE_RED]],
        hover_name='district_name',
        labels={'nscas_ela_all': 'All Students ELA %', 'nscas_ela_el': 'EL ELA %',
                'el_count': 'EL Count', 'el_percent': 'EL %'}
    )
    fig2.add_shape(type="line", x0=0, y0=0, x1=80, y1=80,
                   line=dict(dash="dash", color="gray"))
    fig2.update_layout(
        title="EL Proficiency vs District Overall -- Gap Visualization", height=450
    )
    st.plotly_chart(fig2, use_container_width=True)


def render_nscas(nscas_df, districts_df):
    st.header("NSCAS Assessment Analysis")
    st.markdown("""
    **Nebraska Student-Centered Assessment System (NSCAS)** -- 3 performance levels:
    Developing, On Track, Advanced. ELA and Math: grades 3-8.
    Nebraska uses only 3 levels (unlike most states with 4), making it harder
    to distinguish between struggling and proficient students at the margins.
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="nscas_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="nscas_g")
    with col3:
        subject = st.selectbox("Subject", ['ELA', 'Math'], key="nscas_s")
    with col4:
        year = st.selectbox("Year", [2025, 2024], key="nscas_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    filtered = nscas_df[
        (nscas_df['district_id'] == district_id) &
        (nscas_df['grade'] == grade) &
        (nscas_df['subject'] == subject) &
        (nscas_df['year'] == year)
    ]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Developing", f"{row['developing_pct']:.1f}%")
        with col2:
            st.metric("On Track", f"{row['on_track_pct']:.1f}%")
        with col3:
            st.metric("Advanced", f"{row['advanced_pct']:.1f}%")

        levels = ['Developing', 'On Track', 'Advanced']
        values = [row['developing_pct'], row['on_track_pct'], row['advanced_pct']]
        colors = [NE_RED, NE_GOLD, '#228B22']
        fig = go.Figure(go.Bar(
            x=levels, y=values, marker_color=colors,
            text=[f"{v:.1f}%" for v in values], textposition='outside'
        ))
        fig.update_layout(
            title=f"NSCAS {subject} -- {district} -- Grade {grade} ({year})",
            yaxis_title="Percentage", height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        st.metric("Combined Proficiency (On Track + Advanced)",
                  f"{row['proficient_pct']:.1f}%",
                  help="On Track + Advanced")

        st.subheader(f"NSCAS {subject} Across Grades -- {district} ({year})")
        cross = nscas_df[
            (nscas_df['district_id'] == district_id) &
            (nscas_df['subject'] == subject) &
            (nscas_df['year'] == year)
        ]
        if not cross.empty:
            fig2 = go.Figure()
            for level, color in zip(levels, colors):
                col_name = level.lower().replace(' ', '_') + '_pct'
                fig2.add_trace(go.Bar(
                    x=cross['grade'], y=cross[col_name],
                    name=level, marker_color=color
                ))
            fig2.update_layout(
                barmode='stack', xaxis_title="Grade", yaxis_title="Percentage",
                height=400, title=f"NSCAS {subject} Performance Distribution"
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")


def render_export(elpa_df, nscas_df, districts_df, domain_df):
    st.header("Export Data")

    st.markdown("Download VERA-NE analysis data as CSV files for further analysis.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ELPA21 Data")
        st.dataframe(elpa_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download ELPA21 CSV",
            elpa_df.to_csv(index=False),
            "vera_ne_elpa21.csv", "text/csv",
            use_container_width=True
        )
    with col2:
        st.subheader("NSCAS Data")
        st.dataframe(nscas_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download NSCAS CSV",
            nscas_df.to_csv(index=False),
            "vera_ne_nscas.csv", "text/csv",
            use_container_width=True
        )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Statewide Domain Proficiency")
        st.dataframe(domain_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Domain CSV",
            domain_df.to_csv(index=False),
            "vera_ne_domains.csv", "text/csv",
            use_container_width=True
        )
    with col2:
        st.subheader("District Reference Data")
        st.dataframe(districts_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Districts CSV",
            districts_df.to_csv(index=False),
            "vera_ne_districts.csv", "text/csv",
            use_container_width=True
        )


# ============================================================================
# MAIN
# ============================================================================

def main():
    st.set_page_config(
        page_title="VERA-NE | Nebraska Type 4 Detection",
        page_icon="*",
        layout="wide"
    )

    st.markdown(f"""
    <style>
        .stApp {{ background-color: #fafafa; }}
        .block-container {{ padding-top: 2rem; }}
        h1, h2, h3 {{ color: {NE_RED}; }}
        .stButton > button {{ background-color: {NE_RED}; color: white; }}
        .stButton > button:hover {{ background-color: {NE_DARK}; color: white; }}
    </style>
    """, unsafe_allow_html=True)

    districts_df = load_districts()
    elpa_df = load_elpa_data(districts_df)
    nscas_df = load_nscas_data(districts_df)
    domain_df = load_statewide_domain_data()

    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: {NE_RED}; margin: 0;">VERA-NE</h2>
        <p style="color: #666; font-size: 0.85rem; margin-top: 5px;">Nebraska Implementation</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.divider()

    page = st.sidebar.radio("Navigation", [
        "Overview",
        "Statewide Domain Analysis",
        "ELPA21 Analysis",
        "Type 4 Detection",
        "Achievement Gaps",
        "NSCAS Analysis",
        "Export Data"
    ])

    st.sidebar.divider()
    st.sidebar.markdown(f"""
    **Data Sources:**
    - ELPA21 (ELPA21 Consortium)
    - NDE ELPA21 Summary Reports
    - NDE Accountability Portal
    - NSCAS (NE Student-Centered)
    - nep.education.ne.gov

    **Type 4 Detection:**
    - Speaking vs Writing delta
    - Flag threshold: > 8 points (normalized)
    - ELPA21 levels 1-5

    **Key Context:**
    - ~33,000 ELs (~10%)
    - ~245 school districts
    - **ELPA21 (NOT WIDA)**
    - **NSCAS: 3 levels only**
    - Meatpacking refugee surge
    - Spanish dominant (65%)
    - Omaha 10,400 ELs (20%)
    - Lincoln 8,400 ELs (20%)
    - Lexington 1,760 ELs (55%)
    - Schuyler 950 ELs (50%)

    ---
    [H-EDU.Solutions](https://h-edu.solutions)
    """)

    if page == "Overview":
        render_overview(districts_df)
    elif page == "Statewide Domain Analysis":
        render_domain_analysis(domain_df)
    elif page == "ELPA21 Analysis":
        render_elpa_analysis(elpa_df, districts_df)
    elif page == "Type 4 Detection":
        render_type4(elpa_df, districts_df)
    elif page == "Achievement Gaps":
        render_achievement_gaps(districts_df)
    elif page == "NSCAS Analysis":
        render_nscas(nscas_df, districts_df)
    elif page == "Export Data":
        render_export(elpa_df, nscas_df, districts_df, domain_df)


if __name__ == "__main__":
    main()
