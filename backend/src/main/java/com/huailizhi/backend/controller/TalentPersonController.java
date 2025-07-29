package com.huailizhi.backend.controller;


import com.huailizhi.backend.entity.TalentPerson;
import com.huailizhi.backend.service.TalentPersonService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/talentPerson")
@CrossOrigin(origins = "http://localhost:5173")
public class TalentPersonController {
    @Autowired
    private TalentPersonService talentPersonService;

    @GetMapping("/country/{cntry}")
    public List<TalentPerson> getTop100ByCountry(@PathVariable String cntry){
        return talentPersonService.getTop100ByCountry(cntry);
    }

    // 分页查询国家人才
    @GetMapping("/country/{cntry}/page/{page}")
    public Page<TalentPerson> getByCountryWithPage(
            @PathVariable String cntry,
            @PathVariable int page,
            @RequestParam(defaultValue = "10") int size){
        return talentPersonService.getByCountryWithPage(cntry, page, size);
    }

    // 查询人才详情
    @GetMapping("/{id}")
    public ResponseEntity<TalentPerson> getTalentDetail(@PathVariable Integer id){
        Optional<TalentPerson> talentPerson = talentPersonService.getTalentById(id);
        return talentPerson.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}
