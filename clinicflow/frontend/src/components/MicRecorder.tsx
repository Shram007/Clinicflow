import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";

const MicRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  const start = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    streamRef.current = stream;
    const mr = new MediaRecorder(stream);
    mediaRecorderRef.current = mr;
    chunksRef.current = [];
    mr.ondataavailable = e => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };
    mr.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      setUploading(true);
      const fd = new FormData();
      fd.append("file", blob, "recording.webm");
      const res = await fetch(`/api/voice/upload`, { method: "POST", body: fd });
      const data = await res.json();
      setTranscript(data.transcript || "");
      setUploading(false);
    };
    mr.start();
    setRecording(true);
  };

  const stop = () => {
    mediaRecorderRef.current?.stop();
    streamRef.current?.getTracks().forEach(t => t.stop());
    setRecording(false);
  };

  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach(t => t.stop());
    };
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex gap-3">
        {!recording && (
          <Button size="lg" onClick={start} disabled={uploading}>Start Recording</Button>
        )}
        {recording && (
          <Button size="lg" variant="destructive" onClick={stop}>Stop Recording</Button>
        )}
        {recording && <span className="text-sm text-destructive">Recording…</span>}
        {uploading && <span className="text-sm text-muted-foreground">Uploading…</span>}
      </div>
      <div className="space-y-2">
        <textarea
          className="w-full h-48 rounded-md border p-3"
          placeholder="Transcript"
          value={transcript}
          onChange={e => setTranscript(e.target.value)}
        />
        <div className="flex gap-2">
          <Button size="sm">Run ClinicFlow</Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={async () => {
              if (!transcript) return;
              setSaving(true);
              setSaveMsg(null);
              try {
                const res = await fetch(`/api/visits`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ transcript }),
                });
                if (!res.ok) throw new Error(`Failed to save visit (${res.status})`);
                await res.json();
                setSaveMsg("Visit saved! Check the Visits page.");
              } catch (err: any) {
                setSaveMsg(err?.message ?? "Error saving visit.");
              } finally {
                setSaving(false);
              }
            }}
            disabled={saving || !transcript}
          >
            {saving ? "Saving..." : "Save as Visit"}
          </Button>
        </div>
        {saveMsg && <p className="text-xs text-muted-foreground">{saveMsg}</p>}
      </div>
    </div>
  );
};

export default MicRecorder;
