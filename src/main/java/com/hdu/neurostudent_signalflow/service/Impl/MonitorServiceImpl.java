package com.hdu.neurostudent_signalflow.service.Impl;

import com.hdu.neurostudent_signalflow.monitor.CameraMonitor;
import com.hdu.neurostudent_signalflow.monitor.ScreenMonitor;
import com.hdu.neurostudent_signalflow.service.MonitorService;
import org.springframework.stereotype.Service;

@Service
public class MonitorServiceImpl implements MonitorService {

    @Override
    public void startScreenMonitor() {
        ScreenMonitor.startScreenMonitor();
    }

    @Override
    public void stopScreenMonitor() {
        ScreenMonitor.stopScreenMonitor();
    }

    @Override
    public void startCameraMonitor() {
        CameraMonitor.startCameraMonitor();
    }

    @Override
    public void stopCameraMonitor() {
        CameraMonitor.stopCameraMonitor();
    }
}
