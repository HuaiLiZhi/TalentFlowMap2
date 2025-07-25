package com.huailizhi.backend.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "city_info")
public class City {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;
    private String city_name;
    private int count;
    private double longitude;
    private double latitude;
    private String country;

    public City() {
    }

    public City(int id, String city_name, int count, double longitude, double latitude, String country) {
        this.id = id;
        this.city_name = city_name;
        this.count = count;
        this.longitude = longitude;
        this.latitude = latitude;
        this.country = country;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getCity_name() {
        return city_name;
    }

    public void setCity_name(String city_name) {
        this.city_name = city_name;
    }

    public int getCount() {
        return count;
    }

    public void setCount(int count) {
        this.count = count;
    }

    public double getLongitude() {
        return longitude;
    }

    public void setLongitude(double longitude) {
        this.longitude = longitude;
    }

    public double getLatitude() {
        return latitude;
    }

    public void setLatitude(double latitude) {
        this.latitude = latitude;
    }

    public String getCountry() {
        return country;
    }

    public void setCountry(String country) {
        this.country = country;
    }
}
