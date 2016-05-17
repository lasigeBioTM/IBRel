import itertools

all_entity_types = ("Gene",
                     "Gene_Family",
                     "Box",
                     "Promoter",
                     "RNA",
                     "Protein",
                     "Protein_Family",
                     "Protein_Complex",
                     "Protein_Domain",
                     "Hormone",
                     "Regulatory_Network",
                     "Pathway",
                     "Genotype",
                     "Tissue",
                     "Development_Phase",
                     "Environmental_Factor")

all_entity_groups = {"DNA_Product": ("RNA", "Protein", "Protein_Family", "Protein_Complex", "Protein_Domain"),
                     "DNA": ("Gene", "Gene_Family", "Box", "Promoter"),
                     "Dynamic_Process": ("Regulatory_Network", "Pathway"),
                     "Internal_Factor": ("Tissue", "Development_Phase", "Genotype")}
all_entity_groups["Functional_Molecule"] = all_entity_groups["DNA_Product"] + ("Hormone",)
all_entity_groups["Molecule"] = all_entity_groups["DNA"] + all_entity_groups["Functional_Molecule"]
all_entity_groups["Factor"] = all_entity_groups["Internal_Factor"] + ("Environmental_Factor",)

ds_pair_types = {
    "Binds_To",
"Composes_Primary_Structure",
"Composes_Protein_Complex",
"Exists_At_Stage",
"Is_Involved_In_Process",
"Occurs_In_Genotype",
"Occurs_During",
"Regulates_Accumulation",
"Regulates_Molecule_Activity",
"Regulates_Tissue_Development",
}
pair_types = {
    "Binds_To":
        {"source_role": "Functional_Molecule",
         "source_types": all_entity_groups["Functional_Molecule"],
         "target_role": "Molecule",
         "target_types": all_entity_groups["Molecule"],
         "event": "interaction",
         "keywords": ["bind", "ligand", "interact"]},
    "Composes_Primary_Structure":
        {"source_role": "DNA_Part",
         "source_types": ("Box", "Promoter"),
         "target_role": "DNA",
         "target_types": all_entity_groups["DNA"],
         "event": "composition",
         "keywords": ["primary structure", "domain", "promoter", "site", "element"]},
    "Composes_Protein_Complex":
         {"source_role": "Amino_Acid_Sequence",
          "source_types": ("Protein", "Protein_Family", "Protein_Complex", "Protein_Domain"),
          "target_role": "Protein_Complex",
          "target_types": ("Protein_Complex",),
          "event": "composition",
          "keywords": ["component", "belong", "associate", "presence", "part of"]},
    "Exists_At_Stage":
        {"source_role": "Functional_Molecule",
         "source_types": all_entity_groups["Functional_Molecule"],
         "target_role": "Development",
         "target_types": ("Development_Phase",),
         "event": "wherewhen"},
    "Exists_In_Genotype":
        {"source_role": "Molecule",
         "source_types": all_entity_groups["Molecule"] + ("Biological context",),  # mutually exclusive
         "target_role": "Genotype",
         "target_types": ("Genotype",),
         "event": "wherewhen"},
    "Has_Sequence_Identical_To":
        {"source_role": "Element1",
         "source_types": all_entity_types,
         "target_role": "Element2",
         "target_types": all_entity_types,
         "event": "composition"},
    "Interacts_With":
        {"source_role": "Agent",
         "source_types": all_entity_groups["Molecule"],
         "target_role": "Target",
         "target_types": all_entity_groups["Molecule"],
         "event": "interaction"},
    "Is_Functionally_Equivalent_To":
        {"source_role": "Element1",
         "source_types": all_entity_types,
         "target_role": "Element2",
         "target_types": all_entity_types,
         "event": "function"},
    "Is_Involved_In_Process":
        {"source_role": "Participant",
         "source_types": all_entity_groups["Molecule"],
         "target_role": "Process",
         "target_types": all_entity_groups["Dynamic_Process"],
         "event": "function"},
    "Is_Localized_In":
        {"source_role": "Functional_Molecule",
         "source_types": all_entity_groups["Functional_Molecule"] + all_entity_groups["Dynamic_Process"],
         "target_role": "Target_Tissue",
         "target_types": ("Tissue",),
         "event": "wherewhen"},
    "Is_Member_Of_Family":
        {"source_role": "Element",
         "source_types": ("Gene", "Gene_Family", "Protein", "Protein_Domain", "Protein_Family", "RNA"),
         "target_role": "Family",
         "target_types": ("Gene_Family", "Protein_Family", "RNA"),
         "event": "composition"},
    "Is_Protein_Domain_Of":
        {"source_role": "Domain",
         "source_types": ("Protein_Domain",),
         "target_role": "Product",
         "target_types": all_entity_groups["DNA_Product"],
         "event": "composition"},
    "Occurs_During":
        {"source_role": "Process",
         "source_types": all_entity_groups["Dynamic_Process"],
         "target_role": "Development",
         "target_types": ("Development_Phase",),
         "event": "wherewhen"},
    "Occurs_In_Genotype":
        {"source_role": "Process",
         "source_types": all_entity_groups["Dynamic_Process"],
         "target_role": "Genotype",
         "target_types": ("Genotype",),
         "event": "wherewhen"},
    "Regulates_Accumulation":
        {"source_role": "Agent",
         "source_types": all_entity_types,
         "target_role": "Functional_Molecule",
         "target_types": all_entity_groups["Functional_Molecule"],
         "event": "regulation"},
    "Regulates_Development_Phase":
        {"source_role": "Agent",
         "source_types": all_entity_types,
         "target_role": "Development",
         "target_types": ("Development_Phase",),
         "event": "regulation"},
    "Regulates_Expression":
        {"source_role": "Agent",
         "source_types": all_entity_types,
         "target_role": "DNA",
         "target_types": all_entity_groups["DNA"],
         "event": "regulation"},
    "Regulates_Molecule_Activity":
        {"source_role": "Agent",
         "source_types": all_entity_types,
         "target_role": "Molecule",
         "target_types": all_entity_groups["Molecule"],
         "event": "regulation"},
    "Regulates_Process":
        {"source_role": "Agent",
         "source_types": all_entity_types,
         "target_role": "Process",
         "target_types": all_entity_groups["Dynamic_Process"],
         "event": "regulation"},
    "Regulates_Tissue_Development":
        {"source_role": "Agent",
         "source_types": all_entity_types,
         "target_role": "Target_Tissue",
         "target_types": ("Tissue",),
         "event": "regulation"},
    "Transcribes_Or_Translates_To":
        {"source_role": "Source",
         "source_types": all_entity_groups["DNA"] + ("RNA",),
         "target_role": "Product",
         "target_types": all_entity_groups["DNA_Product"],
         "event": "function"},
    #"Is_Linked_To":
    #    {"source_role": "Agent1",
    #     "source_types": all_entity_types,
    #     "target_role": "Agent2",
    #     "target_types": all_entity_types,
    #     "event": "interaction"}
}
event_types = {"wherewhen": {"subtypes": ['Exists_At_Stage', 'Is_Localized_In', 'Exists_In_Genotype', 'Occurs_In_Genotype', 'Occurs_During']},
               "function": {"subtypes": ['Is_Functionally_Equivalent_To', 'Is_Involved_In_Process', 'Transcribes_Or_Translates_To']},
               "regulation": {"subtypes": ['Regulates_Process', 'Regulates_Expression', 'Regulates_Development_Phase',
                              'Regulates_Accumulation', 'Regulates_Tissue_Development', 'Regulates_Molecule_Activity']},
               "composition": {"subtypes": ['Is_Member_Of_Family', 'Is_Protein_Domain_Of', 'Has_Sequence_Identical_To',
                               'Composes_Primary_Structure', 'Composes_Protein_Complex', ]},
               "interaction": {"subtypes": ['Interacts_With', 'Binds_To']} #'Is_Linked_To']}
               }

for e in event_types:
    stypes = [pair_types[t]["source_types"] for t in event_types[e]["subtypes"]]
    ttypes = [pair_types[t]["target_types"] for t in event_types[e]["subtypes"]]
    event_types[e]["source_types"] = set(itertools.chain.from_iterable(stypes))
    event_types[e]["target_types"] = set(itertools.chain.from_iterable(ttypes))