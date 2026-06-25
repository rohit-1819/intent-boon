package org.onosproject.ngsdn.tutorial;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.osgi.service.component.annotations.Activate;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Deactivate;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;
import org.osgi.service.http.HttpService;

import org.onosproject.net.flow.FlowEntry;
import org.onosproject.net.Device;
import org.onosproject.net.device.DeviceService;
import org.onosproject.net.flow.FlowEntry;
import org.onosproject.net.flow.FlowRule;
import org.onosproject.net.flow.FlowRuleService;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.stream.Collectors;

@Component(immediate = true)
public class QosRestServlet extends HttpServlet {

    private final Logger log = LoggerFactory.getLogger(getClass());
    private static final String SERVLET_PATH = "/ngsdn/qos";
    private final ObjectMapper mapper = new ObjectMapper();

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private HttpService httpService;


    @Activate
    protected void activate() {
        try {
            httpService.registerServlet(SERVLET_PATH, this, null, null);
            log.info("QoS REST servlet registered at {}", SERVLET_PATH);
        } catch (Exception e) {
            log.error("Failed to register QoS servlet", e);
        }
    }

    @Deactivate
    protected void deactivate() {
        httpService.unregister(SERVLET_PATH);
        log.info("QoS REST servlet unregistered");
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws IOException {

        L2BridgingComponent app = AppInstance.component;
        if (app == null) {
       	    sendJson(resp, 503, error("Service not ready"));
            return;
        }
        ObjectNode node = mapper.createObjectNode();
        node.put("policy", app.getCurrentPolicy());
        sendJson(resp, 200, node.toString());
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws IOException {
        L2BridgingComponent app = AppInstance.component;
        if (app == null) {
            sendJson(resp, 503, error("Service not ready"));
            return;
        }
        try {
            String body = req.getReader().lines()
                    .collect(Collectors.joining());
            String type = mapper.readTree(body).get("type").asText();

            switch (type.toLowerCase()) {
                case "video": app.setVideoPriority(); break;
                case "voice": app.setVoicePriority(); break;
                default:
                    sendJson(resp, 400, error("Unknown type: " + type));
                    return;
            }

            ObjectNode node = mapper.createObjectNode();
            node.put("result", "ok");
            node.put("policy", type);
            sendJson(resp, 200, node.toString());

        } catch (Exception e) {
            sendJson(resp, 400, error(e.getMessage()));
        }
    }


    private void sendJson(HttpServletResponse resp, int status, String json)
            throws IOException {
        resp.setStatus(status);
        resp.setContentType("application/json");
        resp.setCharacterEncoding("UTF-8");
        try (PrintWriter writer = resp.getWriter()) {
            writer.write(json);
        }
    }

    private String error(String msg) {
        return "{\"error\":\"" + msg + "\"}";
    }
}

