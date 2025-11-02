package com.hdu.neurostudent_signalflow.service.Impl;

import com.hdu.neurostudent_signalflow.monitor.ScreenMonitor;
import com.hdu.neurostudent_signalflow.service.MonitorService;
import org.springframework.stereotype.Service;

@Service
public class MonitorServiceImpl implements MonitorService {

    @Override
    public void startScreenMonitor() {
        ScreenMonitor.startScreenMonitor();
    }
}
