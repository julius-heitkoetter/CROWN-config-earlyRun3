from __future__ import annotations  # needed for type annotations in > python 3.7

from typing import List

from .producers import electrons as electrons
from .producers import event as event
from .producers import genparticles as genparticles
from .producers import jets as jets
from .producers import met as met
from .producers import muons as muons
from .producers import pairquantities as pairquantities
from .producers import pairselection as pairselection
from .producers import scalefactors as scalefactors
from .producers import triggers as triggers
from .quantities import nanoAOD as nanoAOD
from .quantities import output as q
from .triggersetup import add_earlyRun3TriggerSetup
from .jet_variations import add_jetVariations
from .jec_data import add_jetCorrectionData
from code_generation.configuration import Configuration
from code_generation.modifiers import EraModifier, SampleModifier
from code_generation.rules import AppendProducer, RemoveProducer, ReplaceProducer
from code_generation.systematics import SystematicShift, SystematicShiftByQuantity
from .variations import add_leptonSFShifts  # add_tauVariations

# from .producers import taus as taus
# from .producers import embedding as emb


def build_config(
    era: str,
    sample: str,
    scopes: List[str],
    shifts: List[str],
    available_sample_types: List[str],
    available_eras: List[str],
    available_scopes: List[str],
):
    configuration = Configuration(
        era,
        sample,
        scopes,
        shifts,
        available_sample_types,
        available_eras,
        available_scopes,
    )

    # first add default parameters necessary for all scopes
    configuration.add_config_parameters(
        "global",
        {
            # "RunLumiEventFilter_Quantities": ["event", "luminosityBlock"],
            # "RunLumiEventFilter_Quantity_Types": ["ULong64_t", "UInt_t"],
            # "RunLumiEventFilter_Selections": ["3", "318"],

            "PU_reweighting_file": EraModifier(
                {
                    "2016": "data/pileup/Data_Pileup_2016_271036-284044_13TeVMoriond17_23Sep2016ReReco_69p2mbMinBiasXS.root",
                    "2017": "data/pileup/Data_Pileup_2017_294927-306462_13TeVSummer17_PromptReco_69p2mbMinBiasXS.root",
                    "2018": "data/pileup/Data_Pileup_2018_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18.root",
                }
            ),
            "golden_json_file": EraModifier(
                {
                    "2016": "data/golden_json/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt",
                    "2017": "data/golden_json/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt",
                    "2018": "data/golden_json/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt",
                }
            ),
            "PU_reweighting_hist": "pileup",
            "met_filters": EraModifier(
                {
                    "2018": [
                        "Flag_goodVertices",
                        "Flag_globalSuperTightHalo2016Filter",
                        "Flag_HBHENoiseFilter",
                        "Flag_HBHENoiseIsoFilter",
                        "Flag_EcalDeadCellTriggerPrimitiveFilter",
                        "Flag_BadPFMuonFilter",
                        # "Flag_BadPFMuonDzFilter", # only since nanoAODv9 available
                        "Flag_eeBadScFilter",
                        "Flag_ecalBadCalibFilter",
                    ],
                }
            ),
        },
    )

    # jet base selection:
    configuration.add_config_parameters(
        "global",
        {
            "min_jet_pt": 30,
            "max_jet_eta": 4.7,
            "jet_id": 2,  # second bit is tight JetID
            "jet_puid": 4,  # 0==fail, 4==pass(loose), 6==pass(loose,medium), 7==pass(loose,medium,tight) !check 2016 -> inverted ID
            "jet_puid_max_pt": 50,  # recommended to apply puID only for jets below 50 GeV
            "jet_reapplyJES": False,
            "jet_jes_sources": '{""}',
            "jet_jes_shift": 0,
            "jet_jer_shift": '"nom"',  # or '"up"', '"down"'
            "jet_jec_file": EraModifier(
                {
                    "2016": '"data/jsonpog-integration/POG/JME/2016postVFP_UL/jet_jerc.json.gz"',
                    "2017": '"data/jsonpog-integration/POG/JME/2017_UL/jet_jerc.json.gz"',
                    "2018": '"data/jsonpog-integration/POG/JME/2018_UL/jet_jerc.json.gz"',
                }
            ),
            "jet_jer_tag": EraModifier(
                {
                    "2016preVFP": '"Summer20UL16APV_JRV3_MC"',
                    "2016postVFP": '"Summer20UL16_JRV3_MC"',
                    "2017": '"Summer19UL17_JRV2_MC"',
                    "2018": '"Summer19UL18_JRV2_MC"',
                }
            ),
            "jet_jes_tag_data": '""',
            "jet_jes_tag": EraModifier(
                {
                    "2016preVFP": '"Summer19UL16APV_V7_MC"',
                    "2016postVFP": '"Summer19UL16_V7_MC"',
                    "2017": '"Summer19UL17_V5_MC"',
                    "2018": '"Summer19UL18_V5_MC"',
                }
            ),
            "jet_jec_algo": '"AK4PFchs"',
        },
    )
    # bjet base selection:
    configuration.add_config_parameters(
        "global",
        {
            "min_bjet_pt": 20,
            "max_bjet_eta": EraModifier(
                {
                    "2016": 2.4,
                    "2017": 2.5,
                    "2018": 2.5,
                }
            ),
            "btag_cut": EraModifier(  # medium
                {
                    "2016": 0.3093,
                    "2017": 0.3040,
                    "2018": 0.2783,
                }
            ),
        },
    )

    # muon base selection:
    configuration.add_config_parameters(
        "global",
        {
            "min_muon_pt": 20.0,
            "max_muon_eta": 2.4,
            "max_muon_dxy": 1e9,  # 0.045,
            "max_muon_dz": 1e0,  # 0.2,
            "muon_id": "Muon_tightId",  # "Muon_mediumId",
            "muon_iso_cut": 0.3,
        },
    )

    # electron base selection:
    configuration.add_config_parameters(
        "global",
        {
            "min_ele_pt": 10.0,
            "max_ele_eta": 2.5,
            "max_ele_dxy": 1.e9,  # 0.045,
            "max_ele_dz": 1.e9,  # 0.2,
            "max_ele_iso": 1.e9,  # 0.3
            "ele_id": "Electron_cutBased",  # "Electron_mvaFall17V2noIso_WP90",
            "ele_id_wp": 3,  # Cut-based medium ID
        },
    )

    ###### scope Specifics ######

    # mm scope selection
    configuration.add_config_parameters(
        ["mm"],
        {
            "muon_index_in_pair": 0,
            "min_muon_pt": 25.0,
            "max_muon_eta": 2.4,
            "muon_iso_cut": 0.15,
            "second_muon_index_in_pair": 1,
        },
    )

    # mmet scope selection (muon veto selection):
    configuration.add_config_parameters(
        ["mmet"],
        {
            "muon_index_in_pair": 0,  # dummy index for the selected lepton
            "min_muon_pt": 25.0,
            "max_muon_eta": 2.4,
            "muon_iso_cut": 0.15,

            "min_muon_veto_pt": 10.0,
            "max_muon_veto_eta": 2.4,
            "max_muon_veto_dxy": 1.e9,  # 0.045,
            "max_muon_veto_dz": 1.e9,  # 0.2,
            "muon_veto_id": "Muon_looseId",  # "Muon_mediumId",
            "muon_veto_iso_cut": 1.e9,
            "n_good_muons": 1
        },
    )

    # ee scope selection:
    configuration.add_config_parameters(
        ["ee"],
        {
            "electron_index_in_pair": 0,
            "min_electron_pt": 25.0,
            "max_electron_eta": 2.5,
            "electron_iso_cut": 1e9,
        },
    )

    # emet scope selection:
    configuration.add_config_parameters(
        ["emet"],
        {
            "electron_index_in_pair": 0,
            "min_electron_pt": 25.0,
            "max_electron_eta": 2.5,
            "electron_iso_cut": 1e9,
            "second_electron_index_in_pair": 1,

            "min_electron_veto_pt": 10.0,
            "max_electron_veto_eta": 2.5,
            "max_electron_veto_dxy": 1.e9,  # 0.045,
            "max_electron_veto_dz": 1.e9,  # 0.2,
            "electron_veto_id": "Electron_cutBased",
            "electron_veto_id_wp": 1,
            "electron_veto_iso_cut": 1.e9,
            "n_good_electrons": 1
        },
    )

    # Muon scale factors configuration
    configuration.add_config_parameters(
        ["mm", "mmet"],
        {
            "muon_sf_file": EraModifier(
                {
                    # "2016": "data/jsonpog-integration/POG/MUO/2016postVFP_UL/muon_Z.json.gz",
                    # "2017": "data/jsonpog-integration/POG/MUO/2017_UL/muon_Z.json.gz",
                    "2018": "data/jsonpog-integration/POG/MUO/2018_UL/muon_Z.json.gz",
                }
            ),
            "muon_id_sf_name": "NUM_TightID_DEN_TrackerMuons",
            "muon_iso_sf_name": "NUM_TightRelIso_DEN_TightIDandIPCut",
            "muon_sf_year_id": EraModifier(
                {
                    # "2016": "2016postVFP_UL",
                    # "2017": "2017_UL",
                    "2018": "2018_UL",
                }
            ),
            "muon_sf_varation": "sf",  # "sf" is nominal, "systup"/"systdown" are up/down variations
        },
    )
    # electron scale factors configuration
    configuration.add_config_parameters(
        ["ee", "emet"],
        {
            "ele_sf_file": EraModifier(
                {
                    "2016preVFP": "data/jsonpog-integration/POG/EGM/2016preVFP_UL/electron.json.gz",
                    "2016postVFP": "data/jsonpog-integration/POG/EGM/2016postVFP_UL/electron.json.gz",
                    "2017": "data/jsonpog-integration/POG/EGM/2017_UL/electron.json.gz",
                    "2018": "data/jsonpog-integration/POG/EGM/2018_UL/electron.json.gz",
                }
            ),
            "ele_id_sf_name": "UL-Electron-ID-SF",
            "ele_sf_year_id": EraModifier(
                {
                    "2016preVFP": "2016preVFP",
                    "2016postVFP": "2016postVFP",
                    "2017": "2017",
                    "2018": "2018",
                }
            ),
            "ele_sf_varation": "sf",  # "sf" is nominal, "sfup"/"sfdown" are up/down variations
        },
    )


    ## all scopes misc settings
    configuration.add_config_parameters(
        scopes,
        {
            "deltaR_jet_veto": 0.5,
            "pairselection_min_dR": 0.5,
        },
    )
    ## all scopes MET selection
    configuration.add_config_parameters(
        scopes,
        {
            "propagateLeptons": SampleModifier(
                {"data": False, "emb": False},
                default=True,
            ),
            "propagateJets": SampleModifier(
                {"data": False, "emb": False},
                default=True,
            ),
            "recoil_corrections_file": EraModifier(
                {
                    "2016": "data/recoil_corrections/Type1_PuppiMET_2016.root",
                    "2017": "data/recoil_corrections/Type1_PuppiMET_2017.root",
                    "2018": "data/recoil_corrections/Type1_PuppiMET_2018.root",
                }
            ),
            "recoil_systematics_file": EraModifier(
                {
                    "2016": "data/recoil_corrections/PuppiMETSys_2016.root",
                    "2017": "data/recoil_corrections/PuppiMETSys_2017.root",
                    "2018": "data/recoil_corrections/PuppiMETSys_2018.root",
                }
            ),
            "applyRecoilCorrections": SampleModifier({"wj": True}, default=False),
            "apply_recoil_resolution_systematic": False,
            "apply_recoil_response_systematic": False,
            "recoil_systematic_shift_up": False,
            "recoil_systematic_shift_down": False,
            "min_jetpt_met_propagation": 15,
        },
    )

    configuration.add_config_parameters(
        scopes,
        {
            "ggHNNLOweightsRootfile": "data/htxs/NNLOPS_reweight.root",
            "ggH_generator": "powheg",
            "zptmass_file": EraModifier(
                {
                    "2016": "data/zpt/htt_scalefactors_legacy_2016.root",
                    "2017": "data/zpt/htt_scalefactors_legacy_2017.root",
                    "2018": "data/zpt/htt_scalefactors_legacy_2018.root",
                }
            ),
            "zptmass_functor": "zptmass_weight_nom",
            "zptmass_arguments": "z_gen_mass,z_gen_pt",
        },
    )
    configuration.add_producers(
        "global",
        [
            # event.RunLumiEventFilter,
            event.SampleFlags,
            event.Lumi,
            event.npartons,
            event.MetFilter,
            event.PUweights,
            event.EventGenWeight,
            muons.BaseMuons,
            electrons.BaseElectrons,
            jets.JetEnergyCorrection,
            jets.GoodJets,
            jets.GoodBJets,
            met.MetBasics,

            # event.DiLeptonVeto,
        ],
    )
    ## add prefiring
    if era != "2018":
        configuration.add_producers(
            "global",
            [
                event.PrefireWeight,
            ],
        )
    # common
    configuration.add_producers(
        scopes,
        [
            jets.JetCollection,
            jets.BasicJetQuantities,
            jets.BJetCollection,
            jets.BasicBJetQuantities,
            met.MetCorrections,
            met.PFMetCorrections,
        ],
    )

    configuration.add_producers(
        "mm",
        [
            muons.GoodMuons,
            muons.NumberOfGoodMuons,
            pairselection.ZLLPairSelection,
            pairselection.GoodLLPairFilter,
            pairselection.LVMu1,
            pairselection.LVMu2,
            pairselection.LVMu1Uncorrected,
            pairselection.LVMu2Uncorrected,
            pairquantities.DileptonQuantities,
            pairquantities.DileptonMETQuantities,

            scalefactors.MuonIDIso_SF,
            triggers.MMGenerateSingleMuonTriggerFlags1,
            triggers.MMGenerateSingleMuonTriggerFlags2,

            genparticles.MMGenDiTauPairQuantities,
            genparticles.gen_match_1,
            genparticles.gen_match_2,
        ],
    )

    configuration.add_producers(
        "mmet",
        [
            muons.GoodMuons,
            muons.NumberOfGoodMuons,
            muons.OneGoodMuonSelection,
            pairselection.LVMu1,
            pairselection.LVMu1Uncorrected,
            pairquantities.LepMETQuantities,

            scalefactors.MuonIDIso_SF,
            triggers.MMGenerateSingleMuonTriggerFlags1,

            genparticles.gen_match_1,
            # genparticles.gen_match_2,
        ],
    )

    configuration.add_producers(
        "ee",
        [
            electrons.GoodElectrons,
            electrons.NumberOfGoodElectrons,
            pairselection.ZLLPairSelection,
            pairselection.GoodLLPairFilter,
            pairselection.LVEl1,
            pairselection.LVEl2,
            pairselection.LVEl1Uncorrected,
            pairselection.LVEl2Uncorrected,
            pairquantities.DileptonQuantities,
            pairquantities.DileptonMETQuantities,

            scalefactors.EleID_SF,
            triggers.EEGenerateSingleElectronTriggerFlags1,
            triggers.EEGenerateSingleElectronTriggerFlags2,

            # genparticles.MMGenDiTauPairQuantities,
            genparticles.gen_match_1,
            genparticles.gen_match_2,
        ],
    )

    configuration.add_producers(
        "emet",
        [
            electrons.GoodElectrons,
            electrons.NumberOfGoodElectrons,
            electrons.OneGoodElectronSelection,
            pairselection.LVEl1,
            pairselection.LVEl1Uncorrected,
            pairquantities.LepMETQuantities,

            scalefactors.EleID_SF,
            triggers.EEGenerateSingleElectronTriggerFlags1,

            genparticles.gen_match_1,
            # genparticles.gen_match_2,
        ],
    )


    # modification rules
    configuration.add_modification_rule(
        "global",
        ReplaceProducer(
            producers=[jets.JetEnergyCorrection, jets.JetEnergyCorrection_data],
            samples="data",
        ),
    )
    configuration.add_modification_rule(
        ["mm", "mmet"],
        RemoveProducer(producers=scalefactors.MuonIDIso_SF, samples="data"),
    )
    configuration.add_modification_rule(
        ["ee", "emet"],
        RemoveProducer(producers=scalefactors.EleID_SF, samples="data"),
    )
    configuration.add_modification_rule(
        "global",
        RemoveProducer(
            producers=[event.PUweights, event.EventGenWeight, event.npartons],
            samples=["data"],
        ),
    )

    configuration.add_modification_rule(
        "global",
        AppendProducer(producers=event.JSONFilter, samples=["data"]),
    )

    configuration.add_modification_rule(
        "mm",
        RemoveProducer(
            producers=[
                genparticles.MMGenDiTauPairQuantities,
                genparticles.gen_match_1,
                genparticles.gen_match_2,
            ],
            samples=["data"],
        ),
    )
    configuration.add_modification_rule(
        "mmet",
        RemoveProducer(
            producers=[
                # genparticles.MMGenDiTauPairQuantities,
                genparticles.gen_match_1,
                # genparticles.gen_match_2,
            ],
            samples=["data"],
        ),
    )
    configuration.add_modification_rule(
        "ee",
        RemoveProducer(
            producers=[
                # genparticles.MMGenDiTauPairQuantities,
                genparticles.gen_match_1,
                genparticles.gen_match_2,
            ],
            samples=["data"],
        ),
    )
    configuration.add_modification_rule(
        "emet",
        RemoveProducer(
            producers=[
                # genparticles.MMGenDiTauPairQuantities,
                genparticles.gen_match_1,
                # genparticles.gen_match_2,
            ],
            samples=["data"],
        ),
    )


    # Output contents
    configuration.add_outputs(
        scopes,
        [
            q.is_data,
            q.is_embedding,
            q.is_ttbar,
            q.is_dyjets,
            q.is_wjets,
            q.is_ggh_htautau,
            q.is_vbf_htautau,
            q.is_diboson,

            nanoAOD.run,
            q.lumi,
            nanoAOD.event,
            q.npartons,
            q.puweight,
            q.genweight,

            q.njets,
            q.jpt_1,
            q.jpt_2,
            q.jeta_1,
            q.jeta_2,
            q.jphi_1,
            q.jphi_2,
            q.jtag_value_1,
            q.jtag_value_2,

            q.nbtag,
            q.bpt_1,
            q.bpt_2,
            q.beta_1,
            q.beta_2,
            q.bphi_1,
            q.bphi_2,
            q.btag_value_1,
            q.btag_value_2,

            q.met,
            q.metphi,
            q.pfmet,
            q.pfmetphi,
            q.met_uncorrected,
            q.metphi_uncorrected,
            q.pfmet_uncorrected,
            q.pfmetphi_uncorrected,
            q.metSumEt,
            q.metcov00,
            q.metcov01,
            q.metcov10,
            q.metcov11,

            # q.pzetamissvis,
            # q.mTdileptonMET,
            # q.mt_1,
            # q.mt_2,
            # q.pt_tt,
            # q.pt_ttjj,
            # q.mt_tot,
            # q.genbosonmass,
        ],
    )

    configuration.add_outputs(
        "mm",
        [
            q.nmuons,

            q.pt_1,
            q.eta_1,
            q.phi_1,
            q.mass_1,
            q.dxy_1,
            q.dz_1,
            q.q_1,
            q.iso_1,

            q.pt_2,
            q.eta_2,
            q.phi_2,
            q.mass_2,
            q.dxy_2,
            q.dz_2,
            q.q_2,
            q.iso_2,

            q.gen_pt_1,
            q.gen_eta_1,
            q.gen_phi_1,
            q.gen_mass_1,
            q.gen_pdgid_1,
            q.gen_match_1,

            q.gen_pt_2,
            q.gen_eta_2,
            q.gen_phi_2,
            q.gen_mass_2,
            q.gen_pdgid_2,
            q.gen_match_2,

            q.gen_m_vis,

            q.mjj,
            q.m_vis,
            q.pt_vis,

            triggers.MMGenerateSingleMuonTriggerFlags1.output_group,
            triggers.MMGenerateSingleMuonTriggerFlags2.output_group,
            q.id_wgt_mu_1,
            q.iso_wgt_mu_1,
            q.id_wgt_mu_2,
            q.iso_wgt_mu_2,
        ],
    )

    configuration.add_outputs(
        "mmet",
        [
            q.nmuons,

            q.pt_1,
            q.eta_1,
            q.phi_1,
            q.mass_1,
            q.dxy_1,
            q.dz_1,
            q.q_1,
            q.iso_1,

            q.gen_match_1,

            q.mt_1,

            triggers.MMGenerateSingleMuonTriggerFlags1.output_group,
            q.id_wgt_mu_1,
            q.iso_wgt_mu_1,
        ],
    )

    configuration.add_outputs(
        "ee",
        [
            q.nelectrons,

            q.pt_1,
            q.eta_1,
            q.phi_1,
            q.mass_1,
            q.dxy_1,
            q.dz_1,
            q.q_1,
            q.iso_1,

            q.pt_2,
            q.eta_2,
            q.phi_2,
            q.mass_2,
            q.dxy_2,
            q.dz_2,
            q.q_2,
            q.iso_2,

            # q.gen_pt_1,
            # q.gen_eta_1,
            # q.gen_phi_1,
            # q.gen_mass_1,
            # q.gen_pdgid_1,
            q.gen_match_1,

            # q.gen_pt_2,
            # q.gen_eta_2,
            # q.gen_phi_2,
            # q.gen_mass_2,
            # q.gen_pdgid_2,
            q.gen_match_2,

            # q.gen_m_vis,

            q.mjj,
            q.m_vis,
            q.pt_vis,

            triggers.EEGenerateSingleElectronTriggerFlags1.output_group,
            triggers.EEGenerateSingleElectronTriggerFlags2.output_group,
            q.id_wgt_ele_wpmedium_1,
            q.id_wgt_ele_wpmedium_2,
        ],
    )

    configuration.add_outputs(
        "emet",
        [
            q.nelectrons,

            q.pt_1,
            q.eta_1,
            q.phi_1,
            q.mass_1,
            q.dxy_1,
            q.dz_1,
            q.q_1,
            q.iso_1,

            q.gen_match_1,

            q.mt_1,

            triggers.EEGenerateSingleElectronTriggerFlags1.output_group,
            q.id_wgt_ele_wpmedium_1,
        ],
    )

    #########################
    # Lepton to tau fakes energy scalefactor shifts  #
    #########################
    # if "dyjets" in sample:
    #     configuration.add_shift(
    #         SystematicShift(
    #             name="tauMuFakeEsDown",
    #             shift_config={
    #                 "mt": {
    #                     "tau_mufake_es": "down",
    #                 }
    #             },
    #             producers={"mt": [taus.TauPtCorrection_muFake]},
    #         )
    #     )
    #     configuration.add_shift(
    #         SystematicShift(
    #             name="tauMuFakeEsUp",
    #             shift_config={
    #                 "mt": {
    #                     "tau_mufake_es": "up",
    #                 }
    #             },
    #             producers={"mt": [taus.TauPtCorrection_muFake]},
    #         )
    #     )
    #     configuration.add_shift(
    #         SystematicShift(
    #             name="tauEleFakeEs1prongBarrelDown",
    #             shift_config={
    #                 "et": {
    #                     "tau_elefake_es_DM0_barrel": "down",
    #                 }
    #             },
    #             producers={"et": [taus.TauPtCorrection_eleFake]},
    #         )
    #     )
    #     configuration.add_shift(
    #         SystematicShift(
    #             name="tauEleFakeEs1prongBarrelUp",
    #             shift_config={
    #                 "et": {
    #                     "tau_elefake_es_DM0_barrel": "up",
    #                 }
    #             },
    #             producers={"et": [taus.TauPtCorrection_eleFake]},
    #         )
    #     )
    #     configuration.add_shift(
    #         SystematicShift(
    #             name="tauEleFakeEs1prongEndcapDown",
    #             shift_config={
    #                 "et": {
    #                     "tau_elefake_es_DM0_endcap": "down",
    #                 }
    #             },
    #             producers={"et": [taus.TauPtCorrection_eleFake]},
    #         )
    #     )
    #     configuration.add_shift(
    #         SystematicShift(
    #             name="tauEleFakeEs1prongEndcapUp",
    #             shift_config={
    #                 "et": {
    #                     "tau_elefake_es_DM0_endcap": "up",
    #                 }
    #             },
    #             producers={"et": [taus.TauPtCorrection_eleFake]},
    #         )
    #     )
    #     configuration.add_shift(
    #         SystematicShift(
    #             name="tauEleFakeEs1prong1pizeroBarrelDown",
    #             shift_config={
    #                 "et": {
    #                     "tau_elefake_es_DM1_barrel": "down",
    #                 }
    #             },
    #             producers={"et": [taus.TauPtCorrection_eleFake]},
    #         )
    #     )
    #     configuration.add_shift(
    #         SystematicShift(
    #             name="tauEleFakeEs1prong1pizeroBarrelUp",
    #             shift_config={
    #                 "et": {
    #                     "tau_elefake_es_DM1_barrel": "up",
    #                 }
    #             },
    #             producers={"et": [taus.TauPtCorrection_eleFake]},
    #         )
    #     )
    #     configuration.add_shift(
    #         SystematicShift(
    #             name="tauEleFakeEs1prong1pizeroEndcapDown",
    #             shift_config={
    #                 "et": {
    #                     "tau_elefake_es_DM1_endcap": "down",
    #                 }
    #             },
    #             producers={"et": [taus.TauPtCorrection_eleFake]},
    #         )
    #     )
    #     configuration.add_shift(
    #         SystematicShift(
    #             name="tauEleFakeEs1prong1pizeroEndcapUp",
    #             shift_config={
    #                 "et": {
    #                     "tau_elefake_es_DM1_endcap": "up",
    #                 }
    #             },
    #             producers={"et": [taus.TauPtCorrection_eleFake]},
    #         ),
    #         samples=[
    #             sample
    #             for sample in available_sample_types
    #             if sample not in ["data", "emb", "emb_mc"]
    #         ],
    #     )

    #########################
    # Lepton ID/Iso scale factor shifts, channel dependent
    #########################
    add_leptonSFShifts(configuration)

    #########################
    # Import triggersetup   #
    #########################
    add_earlyRun3TriggerSetup(configuration)

    #########################
    # MET Shifts
    #########################
    configuration.add_shift(
        SystematicShiftByQuantity(
            name="metUnclusteredEnUp",
            quantity_change={
                nanoAOD.MET_pt: "PuppiMET_ptUnclusteredUp",
                nanoAOD.MET_phi: "PuppiMET_phiUnclusteredUp",
            },
            scopes=["global"],
        ),
        samples=[
            sample
            for sample in available_sample_types
            if sample not in ["data", "embedding", "embedding_mc"]
        ],
    )
    configuration.add_shift(
        SystematicShiftByQuantity(
            name="metUnclusteredEnDown",
            quantity_change={
                nanoAOD.MET_pt: "PuppiMET_ptUnclusteredDown",
                nanoAOD.MET_phi: "PuppiMET_phiUnclusteredDown",
            },
            scopes=["global"],
        ),
        samples=[
            sample
            for sample in available_sample_types
            if sample not in ["data", "embedding", "embedding_mc"]
        ],
    )
    #########################
    # Prefiring Shifts
    #########################
    if era != "2018":
        configuration.add_shift(
            SystematicShiftByQuantity(
                name="prefiringDown",
                quantity_change={
                    nanoAOD.prefireWeight: "L1PreFiringWeight_Dn",
                },
                scopes=["global"],
            )
        )
        configuration.add_shift(
            SystematicShiftByQuantity(
                name="prefiringUp",
                quantity_change={
                    nanoAOD.prefireWeight: "L1PreFiringWeight_Up",
                },
                scopes=["global"],
            )
        )
    #########################
    # MET Recoil Shifts
    #########################
    configuration.add_shift(
        SystematicShift(
            name="metRecoilResponseUp",
            shift_config={
                ("mm", "mmet", "ee", "emet"): {
                    "apply_recoil_resolution_systematic": False,
                    "apply_recoil_response_systematic": True,
                    "recoil_systematic_shift_up": True,
                    "recoil_systematic_shift_down": False,
                },
            },
            producers={
                ("mm", "mmet", "ee", "emet"): met.ApplyRecoilCorrections
            },
        ),
        samples=[
            sample
            for sample in available_sample_types
            if sample not in ["data", "embedding", "embedding_mc"]
        ],
    )
    configuration.add_shift(
        SystematicShift(
            name="metRecoilResponseDown",
            shift_config={
                ("mm", "mmet", "ee", "emet"): {
                    "apply_recoil_resolution_systematic": False,
                    "apply_recoil_response_systematic": True,
                    "recoil_systematic_shift_up": False,
                    "recoil_systematic_shift_down": True,
                },
            },
            producers={
                ("mm", "mmet", "ee", "emet"): met.ApplyRecoilCorrections
            },
        ),
        samples=[
            sample
            for sample in available_sample_types
            if sample not in ["data", "embedding", "embedding_mc"]
        ],
    )
    configuration.add_shift(
        SystematicShift(
            name="metRecoilResolutionUp",
            shift_config={
                ("mm", "mmet", "ee", "emet"): {
                    "apply_recoil_resolution_systematic": True,
                    "apply_recoil_response_systematic": False,
                    "recoil_systematic_shift_up": True,
                    "recoil_systematic_shift_down": False,
                },
            },
            producers={
                ("mm", "mmet", "ee", "emet"): met.ApplyRecoilCorrections
            },
        ),
        samples=[
            sample
            for sample in available_sample_types
            if sample not in ["data", "embedding", "embedding_mc"]
        ],
    )
    configuration.add_shift(
        SystematicShift(
            name="metRecoilResolutionDown",
            shift_config={
                ("mm", "mmet", "ee", "emet"): {
                    "apply_recoil_resolution_systematic": True,
                    "apply_recoil_response_systematic": False,
                    "recoil_systematic_shift_up": False,
                    "recoil_systematic_shift_down": True,
                },
            },
            producers={
                ("mm", "mmet", "ee", "emet"): met.ApplyRecoilCorrections
            },
        ),
        samples=[
            sample
            for sample in available_sample_types
            if sample not in ["data", "embedding", "embedding_mc"]
        ],
    )

    #########################
    # Jet energy resolution and jet energy scale
    #########################
    add_jetVariations(configuration, available_sample_types, era)

    #########################
    # Jet energy correction for data
    #########################
    add_jetCorrectionData(configuration, era)

    #########################
    # Finalize and validate the configuration
    #########################
    configuration.optimize()
    configuration.validate()
    configuration.report()
    return configuration.expanded_configuration()
