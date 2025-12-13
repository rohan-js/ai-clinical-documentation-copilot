"""
Clinical guidelines data for the RAG pipeline.
Contains synthetic audiological and clinical guideline snippets for retrieval.
"""

CLINICAL_GUIDELINES = [
    # Hearing Loss Classification Guidelines
    {
        "id": "hl-classification-1",
        "category": "hearing_loss_classification",
        "title": "Degree of Hearing Loss Classification",
        "content": """
Hearing loss is classified by degree based on pure-tone average (PTA) thresholds:
- Normal hearing: -10 to 25 dB HL
- Mild hearing loss: 26 to 40 dB HL - Difficulty hearing soft speech, whispers
- Moderate hearing loss: 41 to 55 dB HL - Difficulty with conversational speech
- Moderately severe: 56 to 70 dB HL - Difficulty understanding speech without amplification
- Severe hearing loss: 71 to 90 dB HL - Can only hear loud sounds
- Profound hearing loss: 91+ dB HL - May only perceive vibrations

Recommendation: Document the degree of hearing loss using standard classification and note the pure-tone average for each ear separately.
        """
    },
    {
        "id": "hl-classification-2",
        "category": "hearing_loss_classification",
        "title": "Types of Hearing Loss",
        "content": """
Types of hearing loss based on location of pathology:
1. Conductive Hearing Loss: Problem in outer or middle ear. Air-bone gap present on audiogram. Often treatable medically or surgically. Common causes: ear infections, otosclerosis, cerumen impaction.

2. Sensorineural Hearing Loss (SNHL): Damage to cochlea or auditory nerve. No air-bone gap. Usually permanent. Common causes: aging (presbycusis), noise exposure, ototoxic medications, genetics.

3. Mixed Hearing Loss: Combination of conductive and sensorineural components. Both air and bone conduction thresholds elevated with air-bone gap.

Recommendation: Clearly document the type of hearing loss and suspected etiology to guide treatment planning.
        """
    },
    
    # Audiological Assessment Guidelines
    {
        "id": "audio-assess-1",
        "category": "audiological_assessment",
        "title": "Comprehensive Audiological Evaluation",
        "content": """
A comprehensive audiological evaluation should include:
1. Case history: onset, progression, associated symptoms (tinnitus, dizziness, otalgia)
2. Otoscopy: visual inspection of ear canal and tympanic membrane
3. Pure-tone audiometry: Air and bone conduction thresholds at 250-8000 Hz
4. Speech audiometry: Speech Recognition Threshold (SRT), Word Recognition Score (WRS)
5. Tympanometry: Middle ear function assessment
6. Acoustic reflexes: Ipsilateral and contralateral at 500, 1000, 2000, 4000 Hz

Recommendation: Document all test results with specific values and note any test modifications or patient reliability concerns.
        """
    },
    {
        "id": "audio-assess-2",
        "category": "audiological_assessment",
        "title": "Audiogram Interpretation",
        "content": """
Key audiogram interpretation points:
- Configuration: flat, sloping, rising, cookie-bite (mid-frequency), notched (noise-induced)
- Symmetry: symmetric (similar between ears) vs asymmetric (>10 dB difference)
- Air-bone gap: Indicates conductive component if gap >10 dB
- Speech audiometry correlation: WRS should correlate with degree of hearing loss

Red flags requiring immediate ENT referral:
- Asymmetric SNHL (>15 dB difference between ears)
- Sudden hearing loss (within 72 hours)
- Progressive hearing loss without clear etiology
- Unilateral tinnitus
- Acoustic neuroma suspicion

Recommendation: Always note configuration, symmetry, and any concerning patterns that warrant further investigation.
        """
    },
    
    # Treatment Recommendations
    {
        "id": "treatment-1",
        "category": "treatment_recommendations",
        "title": "Hearing Aid Candidacy",
        "content": """
Hearing aid candidacy considerations:
- Mild to profound sensorineural hearing loss
- Patient motivation and realistic expectations
- Manual dexterity for device handling
- Cognitive status and ability to adapt to amplification

Hearing aid styles by hearing loss degree:
- Mild to moderate: CIC, ITC, ITE, RIC
- Moderate to severe: ITE, BTE, RIC with power receivers
- Severe to profound: BTE with earmold, power BTE

Recommendation: Document hearing aid recommendation with style, technology level, and features based on patient lifestyle and communication needs.
        """
    },
    {
        "id": "treatment-2",
        "category": "treatment_recommendations",
        "title": "Cochlear Implant Candidacy",
        "content": """
Cochlear implant candidacy criteria (adult):
- Moderate to profound bilateral sensorineural hearing loss
- Limited benefit from appropriately fitted hearing aids
- Word recognition scores typically <50% in best-aided condition
- No medical contraindications
- Realistic expectations and commitment to rehabilitation

Pediatric considerations:
- FDA approved for children 9 months and older
- Earlier implantation (before age 3) associated with better outcomes
- Bilateral implantation recommended when possible

Recommendation: Refer patients meeting candidacy criteria to CI center for comprehensive evaluation.
        """
    },
    
    # Tinnitus Management
    {
        "id": "tinnitus-1",
        "category": "tinnitus_management",
        "title": "Tinnitus Assessment and Management",
        "content": """
Tinnitus assessment should include:
- Characterization: pitch, loudness, type (ringing, buzzing, pulsatile)
- Laterality: unilateral, bilateral, head-centered
- Duration and onset circumstances
- Impact on daily life: sleep, concentration, mood
- Associated symptoms: hearing loss, hyperacusis, dizziness

Management options:
1. Sound therapy: masking, habituation devices
2. Hearing aids: address underlying hearing loss
3. Cognitive behavioral therapy (CBT): address psychological impact
4. Tinnitus Retraining Therapy (TRT): habituation approach
5. Medication: for associated anxiety/depression

Red flags: Pulsatile tinnitus requires vascular workup. Unilateral tinnitus with asymmetric hearing loss requires MRI to rule out acoustic neuroma.
        """
    },
    
    # Vestibular Disorders
    {
        "id": "vestibular-1",
        "category": "vestibular_disorders",
        "title": "Vestibular Assessment",
        "content": """
Common vestibular disorders:
1. BPPV (Benign Paroxysmal Positional Vertigo): Brief positional vertigo, positive Dix-Hallpike. Treatment: canalith repositioning maneuvers.

2. Meniere's Disease: Episodic vertigo, fluctuating hearing loss, tinnitus, aural fullness. Treatment: low-sodium diet, diuretics, vestibular rehabilitation.

3. Vestibular Neuritis/Labyrinthitis: Acute severe vertigo, may have hearing loss (labyrinthitis). Treatment: vestibular rehabilitation, short-term vestibular suppressants.

Vestibular function tests: VNG/ENG, rotary chair, VEMP, vHIT

Recommendation: Document episodic nature, triggers, associated symptoms, and functional impact for vestibular complaints.
        """
    },
    
    # Pediatric Audiology
    {
        "id": "pediatric-1",
        "category": "pediatric_audiology",
        "title": "Pediatric Hearing Assessment",
        "content": """
Pediatric audiological assessment by age:
- Newborn to 6 months: ABR, OAE (newborn hearing screening follow-up)
- 6 months to 2 years: VRA (Visual Reinforcement Audiometry)
- 2-5 years: CPA (Conditioned Play Audiometry)
- 5+ years: Conventional audiometry with speech testing

Early intervention is critical:
- All infants should have hearing screening by 1 month
- Diagnosis completed by 3 months
- Intervention started by 6 months (1-3-6 guidelines)

Recommendation: Document developmental milestones and speech/language development relative to hearing status.
        """
    },
    
    # Follow-up Protocols
    {
        "id": "followup-1",
        "category": "follow_up_protocols",
        "title": "Audiological Follow-up Guidelines",
        "content": """
Recommended follow-up intervals:
- New hearing aid users: 2 weeks, 1 month, 3 months, then annually
- Stable hearing loss (no aids): Annual monitoring
- Progressive/fluctuating loss: Every 3-6 months
- Post-cochlear implant: Per CI center protocol
- Pediatric patients: Every 6 months minimum

Each follow-up should include:
- Threshold monitoring (compare to baseline)
- Device check if applicable
- Communication needs assessment
- Counseling on hearing conservation

Recommendation: Document any threshold changes with comparison to baseline and adjust management plan accordingly.
        """
    },
    
    # Hearing Conservation
    {
        "id": "conservation-1",
        "category": "hearing_conservation",
        "title": "Noise-Induced Hearing Loss Prevention",
        "content": """
Noise exposure guidelines:
- Safe exposure limit: 85 dBA for 8 hours (OSHA PEL)
- 3 dB exchange rate: For every 3 dB increase, halve the exposure time
- 90 dB: Max 2 hours; 100 dB: Max 15 minutes; 110 dB: Max 1 minute

Prevention strategies:
1. Engineering controls: noise reduction at source
2. Administrative controls: rotation, breaks, distance
3. Hearing protection: earplugs (NRR 15-30), earmuffs (NRR 20-30)
4. Annual monitoring audiograms for noise-exposed workers

Signs of noise-induced hearing loss:
- Audiometric notch at 3000-6000 Hz (typically 4000 Hz)
- History of noise exposure
- Gradual onset, bilateral, symmetric

Recommendation: Counsel all patients on hearing conservation and document noise exposure history.
        """
    },
    
    # Documentation Standards
    {
        "id": "documentation-1",
        "category": "documentation_standards",
        "title": "Clinical Documentation Best Practices",
        "content": """
Essential documentation elements for audiology:
1. Chief complaint in patient's words
2. Relevant history: otologic, medical, noise exposure, family history
3. Test results with specific values (not just "normal" or "abnormal")
4. Clinical interpretation of findings
5. Diagnosis using appropriate terminology
6. Treatment recommendations with rationale
7. Patient counseling topics covered
8. Follow-up plan with timeline

SOAP note format is recommended:
- Subjective: patient-reported symptoms and history
- Objective: test results and clinical observations
- Assessment: clinical interpretation and diagnosis
- Plan: treatment recommendations and follow-up

Recommendation: Use standardized terminology and include specific measurements for all audiometric data.
        """
    },
    
    # Ototoxicity Monitoring
    {
        "id": "ototoxicity-1",
        "category": "ototoxicity_monitoring",
        "title": "Ototoxicity Monitoring Protocol",
        "content": """
Ototoxic medications requiring monitoring:
- Aminoglycosides (gentamicin, tobramycin, amikacin)
- Platinum-based chemotherapy (cisplatin, carboplatin)
- Loop diuretics (furosemide, ethacrynic acid)
- High-dose aspirin and NSAIDs

Monitoring protocol:
1. Baseline audiogram before treatment begins
2. Extended high-frequency audiometry (up to 20,000 Hz) when possible
3. DPOAEs for early detection of cochlear changes
4. Serial monitoring during treatment (weekly for aminoglycosides)
5. Post-treatment follow-up at 1, 3, 6 months

Significant change criteria:
- ≥20 dB shift at any frequency
- ≥10 dB shift at two consecutive frequencies
- Loss of response at three consecutive frequencies

Recommendation: Document baseline hearing status and monitor regularly. Report ototoxic changes to prescribing physician promptly.
        """
    },
    
    # Aural Rehabilitation
    {
        "id": "aural-rehab-1",
        "category": "aural_rehabilitation",
        "title": "Aural Rehabilitation Components",
        "content": """
Comprehensive aural rehabilitation includes:
1. Amplification: Appropriate hearing technology selection and fitting
2. Auditory training: Formal programs to improve speech perception
3. Communication strategies: Assertive communication, environmental modifications
4. Counseling: Adjustment to hearing loss, realistic expectations
5. Family involvement: Communication partner training
6. Assistive devices: ALDs, captioned phones, alerting systems

Key outcome measures:
- Speech perception testing in quiet and noise
- Self-assessment questionnaires (APHAB, HHIE, IOI-HA)
- Real-ear measurements for hearing aid verification
- Patient satisfaction and quality of life measures

Recommendation: Develop individualized rehabilitation plan addressing patient's specific communication needs and goals.
        """
    }
]


def get_all_guidelines() -> list:
    """Return all clinical guideline snippets."""
    return CLINICAL_GUIDELINES


def get_guidelines_by_category(category: str) -> list:
    """Return guidelines filtered by category."""
    return [g for g in CLINICAL_GUIDELINES if g["category"] == category]


def get_guideline_texts() -> list:
    """Return just the content text for embedding."""
    return [
        f"{g['title']}: {g['content']}"
        for g in CLINICAL_GUIDELINES
    ]


def get_guideline_ids() -> list:
    """Return guideline IDs for ChromaDB."""
    return [g["id"] for g in CLINICAL_GUIDELINES]


def get_guideline_metadata() -> list:
    """Return metadata for each guideline."""
    return [
        {"category": g["category"], "title": g["title"]}
        for g in CLINICAL_GUIDELINES
    ]
