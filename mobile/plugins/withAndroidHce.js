const {
  AndroidConfig,
  createRunOncePlugin,
  withAndroidManifest,
  withDangerousMod,
} = require("@expo/config-plugins");
const fs = require("fs");
const path = require("path");

const SERVICE_CLASS = "com.itsecrnd.rtnhceandroid.HCEService";

function ensureArray(value) {
  if (!value) {
    return [];
  }

  return Array.isArray(value) ? value : [value];
}

function addUsesPermission(manifest, permissionName) {
  manifest["uses-permission"] = ensureArray(manifest["uses-permission"]);

  const exists = manifest["uses-permission"].some(
    (entry) => entry?.$?.["android:name"] === permissionName
  );

  if (!exists) {
    manifest["uses-permission"].push({
      $: { "android:name": permissionName },
    });
  }
}

function addUsesFeature(manifest, featureName) {
  manifest["uses-feature"] = ensureArray(manifest["uses-feature"]);

  const exists = manifest["uses-feature"].some(
    (entry) => entry?.$?.["android:name"] === featureName
  );

  if (!exists) {
    manifest["uses-feature"].push({
      $: {
        "android:name": featureName,
        "android:required": "false",
      },
    });
  }
}

function ensureHceService(mainApplication) {
  mainApplication.service = ensureArray(mainApplication.service);

  const exists = mainApplication.service.some(
    (service) => service?.$?.["android:name"] === SERVICE_CLASS
  );

  if (!exists) {
    mainApplication.service.push({
      $: {
        "android:name": SERVICE_CLASS,
        "android:exported": "true",
        "android:enabled": "true",
        "android:permission": "android.permission.BIND_NFC_SERVICE",
      },
      "intent-filter": [
        {
          action: [
            {
              $: {
                "android:name": "android.nfc.cardemulation.action.HOST_APDU_SERVICE",
              },
            },
          ],
          category: [
            {
              $: {
                "android:name": "android.intent.category.DEFAULT",
              },
            },
          ],
        },
      ],
      "meta-data": [
        {
          $: {
            "android:name": "android.nfc.cardemulation.host_apdu_service",
            "android:resource": "@xml/aid_list",
          },
        },
      ],
    });
  }
}

function buildAidListXml(aids, requireDeviceUnlock) {
  const filters = aids
    .map((aid) => `    <aid-filter android:name="${aid}" />`)
    .join("\n");

  return `<?xml version="1.0" encoding="utf-8"?>
<host-apdu-service xmlns:android="http://schemas.android.com/apk/res/android"
  android:description="@string/app_name"
  android:requireDeviceUnlock="${requireDeviceUnlock ? "true" : "false"}">
  <aid-group android:category="other" android:description="@string/app_name">
${filters}
  </aid-group>
</host-apdu-service>
`;
}

function withAndroidHce(config, props = {}) {
  const aids = Array.isArray(props.aids) && props.aids.length > 0 ? props.aids : ["F001020304"];
  const requireDeviceUnlock = !!props.requireDeviceUnlock;

  config = withAndroidManifest(config, (configWithManifest) => {
    const manifest = configWithManifest.modResults.manifest;
    addUsesPermission(manifest, "android.permission.NFC");
    addUsesFeature(manifest, "android.hardware.nfc.hce");

    const mainApplication = AndroidConfig.Manifest.getMainApplicationOrThrow(manifest);
    ensureHceService(mainApplication);

    return configWithManifest;
  });

  config = withDangerousMod(config, ["android", async (configWithDangerousMod) => {
    const projectRoot = configWithDangerousMod.modRequest.projectRoot;
    const xmlDir = path.join(projectRoot, "android", "app", "src", "main", "res", "xml");
    const aidListPath = path.join(xmlDir, "aid_list.xml");

    await fs.promises.mkdir(xmlDir, { recursive: true });
    await fs.promises.writeFile(
      aidListPath,
      buildAidListXml(aids, requireDeviceUnlock),
      "utf8"
    );

    return configWithDangerousMod;
  }]);

  return config;
}

const pkg = require("../package.json");

module.exports = createRunOncePlugin(withAndroidHce, "withAndroidHce", pkg.version);