package com.huailizhi.backend.repository;

import com.huailizhi.backend.entity.TalentPerson;
import org.springframework.data.domain.Page;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.domain.Pageable;

import java.util.List;

public interface TalentPersonRepository extends JpaRepository<TalentPerson, Integer> {
    // 根据国家代码查询人员

    Page<TalentPerson> findByCntryOrderByRankAllAsc(String cntry, Pageable pageable);
}
