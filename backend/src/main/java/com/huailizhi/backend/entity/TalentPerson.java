package com.huailizhi.backend.entity;

import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "talent_persons")
public class TalentPerson {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(nullable = false)
    private String authfull;

    @Column(name = "inst_name")
    private String instName;

    @Column(name = "cntry")
    private String cntry;

    @Column(name = "np6023")
    private Integer np6023;

    @Column(name = "firstyr")
    private Integer firstYear;

    @Column(name = "lastyr")
    private Integer lastYear;

    @Column(name = "rank_ns")
    private Integer rankNs;

    @Column(name = "nc9623_ns")
    private Integer nc9623Ns;

    @Column(name = "h23_ns")
    private Integer h23Ns;

    @Column(name = "hm23_ns")
    private Double hm23Ns;

    @Column(name = "nps_ns")
    private Integer npsNs;

    @Column(name = "ncs_ns")
    private Integer ncsNs;

    @Column(name = "cpsf_ns")
    private Integer cpsfNs;

    @Column(name = "ncsf_ns")
    private Integer ncsfNs;

    @Column(name = "npsfl_ns")
    private Integer npsflNs;

    @Column(name = "ncsfl_ns")
    private Integer ncsflNs;

    @Column(name = "c_ns")
    private Double cNs;

    @Column(name = "npciting_ns")
    private Integer npcitingNs;

    @Column(name = "cprat_ns")
    private Double cpratNs;

    @Column(name = "np6023_cited9623_ns")
    private Integer np6023Cited9623Ns;

    @Column(name = "self_pct")
    private Double selfPct;

    @Column(name = "rank_all")
    private Integer rankAll;

    @Column(name = "nc9623_all")
    private Integer nc9623All;

    @Column(name = "h23_all")
    private Integer h23All;

    @Column(name = "hm23_all")
    private Double hm23All;

    @Column(name = "nps_all")
    private Integer npsAll;

    @Column(name = "ncs_all")
    private Integer ncsAll;

    @Column(name = "cpsf_all")
    private Integer cpsfAll;

    @Column(name = "ncsf_all")
    private Integer ncsfAll;

    @Column(name = "npsfl_all")
    private Integer npsflAll;

    @Column(name = "ncsfl_all")
    private Integer ncsflAll;

    @Column(name = "c_all")
    private Double cAll;

    @Column(name = "npciting_all")
    private Integer npcitingAll;

    @Column(name = "cprat_all")
    private Double cpratAll;

    @Column(name = "np6023_cited9623_all")
    private Integer np6023Cited9623All;

    @Column(name = "np6023_rw")
    private Integer np6023Rw;

    @Column(name = "nc9623_to_rw")
    private Integer nc9623ToRw;

    @Column(name = "nc9623_rw")
    private Integer nc9623Rw;

    @Column(name = "sm_subfield_1")
    private String smSubfield1;

    @Column(name = "sm_subfield_1_frac")
    private Double smSubfield1Frac;

    @Column(name = "sm_subfield_2")
    private String smSubfield2;

    @Column(name = "sm_subfield_2_frac")
    private Double smSubfield2Frac;

    @Column(name = "sm_field")
    private String smField;

    @Column(name = "sm_field_frac")
    private Double smFieldFrac;

    @Column(name = "rank_sm_subfield_1")
    private Integer rankSmSubfield1;

    @Column(name = "rank_sm_subfield_1_ns")
    private Integer rankSmSubfield1Ns;

    @Column(name = "sm_subfield_1_count")
    private Integer smSubfield1Count;

}
