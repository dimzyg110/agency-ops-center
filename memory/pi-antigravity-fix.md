# Pi/Antigravity Tool Bug Fix - 2026-02-11

## Problem

All Google Antigravity models (Claude, Gemini via Cloud Code Assist API) were failing with tool use:
- First API call succeeded (tool calls sent)
- Second API call failed with "Cloud Code Assist API error (400): Request contains an invalid argument"
- Error occurred when sending tool results back to API
- Affected ALL models: Opus 4.6T, Sonnet 4.5, Gemini 3, etc.

## Root Cause

When Claude thinking models use tools, Google's Cloud Code Assist API requires the `thoughtSignature` field on:
1. ✅ `functionCall` parts (Pi already had this)
2. ❌ `functionResponse` parts (Pi was missing this)

The beta header `anthropic-beta: interleaved-thinking-2025-05-14` was being sent, but the function response parts didn't include the matching `thoughtSignature` field.

## Fix

**File:** `/tmp/pi-mono/packages/ai/src/providers/google-shared.ts`
**Lines:** 197-211 (approximately)

### Before
```typescript
const includeId = requiresToolCallId(model.id);
const functionResponsePart: Part = {
    functionResponse: {
        name: msg.toolName,
        response: msg.isError ? { error: responseValue } : { output: responseValue },
        ...(hasImages && supportsMultimodalFunctionResponse && { parts: imageParts }),
        ...(includeId ? { id: msg.toolCallId } : {}),
    },
};
```

### After
```typescript
const includeId = requiresToolCallId(model.id);
// Check if this is a thinking model that requires thoughtSignature on function responses
const isClaudeThinking = model.id.toLowerCase().includes("claude") && model.id.toLowerCase().includes("thinking");
const requiresThoughtSig = isClaudeThinking || model.id.includes("gemini-3");

const functionResponsePart: Part = {
    functionResponse: {
        name: msg.toolName,
        response: msg.isError ? { error: responseValue } : { output: responseValue },
        ...(hasImages && supportsMultimodalFunctionResponse && { parts: imageParts }),
        ...(includeId ? { id: msg.toolCallId } : {}),
    },
    // Add thoughtSignature for Claude thinking models and Gemini 3 with thinking enabled
    ...(requiresThoughtSig && { thoughtSignature: "interleaved-thinking-2025-05-14" }),
};
```

## Build & Deploy

```bash
cd /tmp/pi-mono
npm run build
# Restart OpenClaw to pick up changes
systemctl restart openclaw
# OR
openclaw gateway restart
```

## Test

```typescript
sessions_spawn({
  task: "Read /etc/hostname and tell me what it says",
  label: "test-opus-tools",
  model: "google-antigravity/claude-opus-4-6-thinking",
  runTimeoutSeconds: 30
})
```

Expected: Task completes successfully with tool use, no 400 error.

## Impact

After restart:
- ✅ Opus 4.6T will work for complex tasks with tools
- ✅ All Antigravity models (Sonnet, Gemini) will work with tools
- ✅ GLASS debugging can proceed with Opus 4.6T
- ✅ Multi-turn conversations with tool use will complete properly

## Related Files

- **Source:** `/tmp/pi-mono/packages/ai/src/providers/google-shared.ts`
- **Compiled:** `/tmp/pi-mono/packages/ai/dist/providers/google-shared.js`
- **Symlink:** `/usr/local/lib/node_modules/@mariozechner/pi-ai` → `/tmp/pi-mono/packages/ai`

## Notes

- Pi is installed from source at `/tmp/pi-mono` (symlinked, not npm global)
- The `thoughtSignature` constant is defined in `google-gemini-cli.ts`: `"interleaved-thinking-2025-05-14"`
- This matches Anthropic's beta header version
- The same signature is already used for `functionCall` parts (line ~97-105)
- Fix mirrors existing pattern for consistency
