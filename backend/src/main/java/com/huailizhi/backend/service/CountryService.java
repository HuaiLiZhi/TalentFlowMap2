package com.huailizhi.backend.service;

import com.huailizhi.backend.entity.Country;
import com.huailizhi.backend.repository.CountryRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CountryService {
    @Autowired
    private CountryRepository countryRepository;

    public List<Country> getAllCities(){
        return countryRepository.findAll();
    }
}
