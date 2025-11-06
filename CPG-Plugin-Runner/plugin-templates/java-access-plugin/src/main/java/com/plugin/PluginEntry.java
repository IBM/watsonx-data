package com.plugin;

import org.pf4j.Plugin;
import org.pf4j.PluginWrapper;

public class PluginEntry extends Plugin {
    public PluginEntry(PluginWrapper wrapper) {
        super(wrapper);
    }

    @Override
    public void start() {
        System.out.println("[PluginEntry] Plugin started");
    }

    @Override
    public void stop() {
        System.out.println("[PluginEntry] Plugin stopped");
    }
}
