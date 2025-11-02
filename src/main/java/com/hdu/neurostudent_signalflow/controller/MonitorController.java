package com.hdu.neurostudent_signalflow.controller;

import com.hdu.neurostudent_signalflow.service.MonitorService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;

@RestController
@RequestMapping("/monitor")
public class MonitorController {
    @Resource
    private MonitorService monitorService;

    @GetMapping("/startScreenMonitor")
    public void playMusic() {
        monitorService.startScreenMonitor();
    }
}
