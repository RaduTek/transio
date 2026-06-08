import Constants, { ExecutionEnvironment } from "expo-constants";
import { getSavedTokenAsync } from "@/helpers/auth";

type HceEvent = {
  type: string;
  arg?: string;
};

type HceSubscription = {
  remove: () => void;
};

type NativeHceModuleType = {
  onEvent: (callback: (event: HceEvent) => void | Promise<void>) => HceSubscription;
  beginSession: () => Promise<void>;
  startHCE: () => Promise<void>;
  respondAPDU: (handle: string | null, responseHex: string) => Promise<void>;
};

export type HceTapResult = {
  success: boolean;
  reason?: "missing-token" | "native-error";
};

const APDU_STATUS_OK = "9000";
const APDU_STATUS_NOT_FOUND = "6A82";

export function isExpoGoRuntime(): boolean {
  return Constants.executionEnvironment === ExecutionEnvironment.StoreClient;
}

function toHexUtf8(value: string): string {
  return Array.from(value)
    .map((char) => char.charCodeAt(0).toString(16).padStart(2, "0"))
    .join("");
}

async function getNativeHceModule(): Promise<NativeHceModuleType | null> {
  try {
    const moduleExports: any = await import("@icedevml/react-native-host-card-emulation");
    const nativeModule: NativeHceModuleType | undefined =
      moduleExports?.NativeHCEModule ??
      moduleExports?.default?.NativeHCEModule ??
      moduleExports?.default;

    if (nativeModule && typeof nativeModule.beginSession === "function") {
      return nativeModule;
    }

    return null;
  } catch {
    return null;
  }
}

async function buildTokenResponseApduHex(): Promise<{ responseHex: string; success: boolean }> {
  try {
    const token = await getSavedTokenAsync();
    return {
      responseHex: `${toHexUtf8(token)}${APDU_STATUS_OK}`,
      success: true,
    };
  } catch {
    return {
      responseHex: APDU_STATUS_NOT_FOUND,
      success: false,
    };
  }
}

export function initializeHceListener(
  onTapResult: (result: HceTapResult) => void
): { cleanup: () => void; active: boolean } {
  if (isExpoGoRuntime()) {
    return { cleanup: () => {}, active: false };
  }

  let subscription: HceSubscription | null = null;
  let disposed = false;

  void (async () => {
    const nativeHceModule = await getNativeHceModule();
    if (!nativeHceModule || disposed) {
      return;
    }

    subscription = nativeHceModule.onEvent(async (event) => {
      try {
        switch (event.type) {
          case "sessionStarted": {
            await nativeHceModule.startHCE();
            break;
          }
          case "received": {
            const tokenApdu = await buildTokenResponseApduHex();
            await nativeHceModule.respondAPDU(null, tokenApdu.responseHex);
            onTapResult(
              tokenApdu.success
                ? { success: true }
                : { success: false, reason: "missing-token" }
            );
            break;
          }
          default:
            break;
        }
      } catch {
        onTapResult({ success: false, reason: "native-error" });
      }
    });

    nativeHceModule.beginSession().catch(() => {
      onTapResult({ success: false, reason: "native-error" });
    });
  })();

  return {
    cleanup: () => {
      disposed = true;
      subscription?.remove();
    },
    active: true,
  };
}