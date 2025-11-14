package com.plugin;

import com.cpg.plugin.AccessEvaluationPlugin;
import com.cpg.plugin.dto.EvaluationStatus;
import com.cpg.plugin.dto.Resource;
import com.cpg.plugin.dto.PluginEvaluationRequest;
import com.cpg.plugin.dto.PluginEvaluationResponse;
import com.cpg.plugin.dto.ResourceEvaluationResult;

import org.pf4j.Extension;

import java.io.IOException;
import java.io.InputStream;
import java.util.*;

/**
 * Example AccessEvaluationPlugin implementation.
 * Keep or replace the logic; this compiles against API classes coming from cpg.jar.
 */

@Extension
public class Plugin implements AccessEvaluationPlugin {

    private static final String pluginId;

    // Static block: Load pluginId once from plugin.properties
    static {
        String id = "unknown-plugin";
        try (InputStream input = Plugin.class.getClassLoader().getResourceAsStream("plugin.properties")) {
            if (input != null) {
                Properties props = new Properties();
                props.load(input);
                id = props.getProperty("plugin.id", id);
            } else {
                System.err.println("[PluginEntry] plugin.properties not found in classpath!");
            }
        } catch (IOException e) {
            System.err.println("[PluginEntry] Failed to read plugin.properties: " + e.getMessage());
        }
        pluginId = id;
        System.out.println("[PluginEntry] Loaded plugin_id: " + pluginId);
    }

       /* -------------------------------------------------------------
        *  In the following section, you are welcome to add your own code logic. 
        *  Please do not alter the basic API structure (Request and Response). 
        * ------------------------------------------------------------- */
    @Override
    public List<PluginEvaluationResponse> evaluate(List<PluginEvaluationRequest> accessRequests) {
        List<PluginEvaluationResponse> pluginResponses = new ArrayList<>();

        try {
            for (PluginEvaluationRequest request : accessRequests) {
                String username = request.getUsername();
                System.out.println("[PluginEntry] Evaluating for user: " + username);

                List<ResourceEvaluationResult> resourceResults = new ArrayList<>();

                // Process each resource in the request
                for (Resource resource : request.getResources()) {
                    ResourceEvaluationResult result = new ResourceEvaluationResult();
                    result.setResourceName(resource.getResourceName());
                    result.setResourceType(resource.getResourceType());
                    result.setActions(resource.getActions());

                    // Simulate allow/deny logic per action
                    List<Map<String, String>> actionsResult = new ArrayList<>();
                    Map<String, String> actionMap = new HashMap<>();
                    for (String action : resource.getActions()) {
                        // Example rule: Allow all actions for demo
                        actionMap.put(action, "true");
                    }
                    actionsResult.add(actionMap);
                    result.setActionsResult(actionsResult);

                    // Optional transforms (not used here)
                    result.setTransformColumns(null);
                    result.setTransformRows(null);

                    resourceResults.add(result);
                }

                // Build plugin-level response
                PluginEvaluationResponse pluginResponse = new PluginEvaluationResponse();
                pluginResponse.setPluginId(pluginId);
                pluginResponse.setStatus(EvaluationStatus.SUCCESS);
                pluginResponse.setError(null);
                pluginResponse.setResources(resourceResults);

                pluginResponses.add(pluginResponse);
            }
        } catch (Exception e) {
            // Handle errors gracefully at plugin-level
            PluginEvaluationResponse errorResponse = new PluginEvaluationResponse();
            errorResponse.setPluginId(pluginId);
            errorResponse.setStatus(EvaluationStatus.ERROR);
            errorResponse.setError("Unexpected error: " + e.getMessage());
            errorResponse.setResources(Collections.emptyList());

            pluginResponses.add(errorResponse);
        }

        System.out.println("[PluginEntry] Returning plugin responses: " + pluginResponses);
        return pluginResponses;
    }
}