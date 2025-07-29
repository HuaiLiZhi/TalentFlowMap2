package com.huailizhi.backend.service;

import com.huailizhi.backend.entity.TalentPerson;
import com.huailizhi.backend.repository.TalentPersonRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import org.springframework.data.domain.Pageable;
import java.util.List;
import java.util.Optional;

@Service
public class TalentPersonService {
    @Autowired
    private TalentPersonRepository talentPersonRepository;


    public List<TalentPerson> getTop100ByCountry(String cntry){
        Pageable top100 = PageRequest.of(0, 100);
        Page<TalentPerson> page = talentPersonRepository.findByCntryOrderByRankAllAsc(cntry, top100);
        return page.getContent();
    }

    public Page<TalentPerson> getByCountryWithPage(String cntry, int page, int size){
        Pageable pageable = PageRequest.of(page - 1, size);
        return talentPersonRepository.findByCntryOrderByRankAllAsc(cntry, pageable);
    }

    public Optional<TalentPerson> getTalentById(Integer id) {
        return talentPersonRepository.findById(id);
    }
}
