package com.building;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.mybatis.spring.annotation.MapperScan;

@SpringBootApplication(scanBasePackages = {"com.building", "com.ship"})
@EnableConfigurationProperties
@MapperScan({"com.building.mapper", "com.ship.mapper"})
public class FloorDesignApplication {

    public static void main(String[] args) {
        SpringApplication.run(FloorDesignApplication.class, args);
    }
}
