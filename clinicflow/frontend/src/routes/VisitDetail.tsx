import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import PageContainer from "@/components/PageContainer";

type VisitDetail = {
  id: number;
  title: string;
  date: string;
  summary: string;
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
};

const VisitDetailPage = () => {
  const { id } = useParams();
  const [visit, setVisit] = useState<VisitDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // audio state
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [audioLoading, setAudioLoading] = useState(false);
  const [audioError, setAudioError] = useState<string | null>(null);

  useEffect(() => {
    async function loadVisit() {
      try {
        setError(null);
        setLoading(true);

        const res = await fetch(`http://localhost:8000/api/visits/${id}`);
        if (!res.ok) throw new Error(`Failed to load visit (status ${res.status})`);
        const data = await res.json();
        setVisit(data);
      } catch (err: any) {
        setError(err?.message ?? "Unknown error");
      } finally {
        setLoading(false);
      }
    }

    if (id) loadVisit();
  }, [id]);

  async function handlePlaySummary() {
    if (!id) return;

    try {
      setAudioError(null);
      setAudioLoading(true);

      const res = await fetch(`http://localhost:8000/api/visits/${id}/summary_audio`);
      if (!res.ok) throw new Error(`Failed to fetch audio (status ${res.status})`);

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);

      // revoke old url to avoid memory leaks
      if (audioUrl) URL.revokeObjectURL(audioUrl);

      setAudioUrl(url);
    } catch (err: any) {
      setAudioError(err?.message ?? "Error fetching audio.");
    } finally {
      setAudioLoading(false);
    }
  }

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-4">
        <Link to="/visits" className="text-sm text-slate-600 hover:underline">
          ← Back to Visits
        </Link>

        <button
          onClick={handlePlaySummary}
          disabled={audioLoading}
          className="px-3 py-2 rounded bg-indigo-600 text-white text-sm disabled:opacity-50"
        >
          {audioLoading ? "Generating..." : "▶ Play Audio Summary"}
        </button>
      </div>

      {audioError && <p className="text-sm text-red-600 mb-3">Audio error: {audioError}</p>}
      {audioUrl && (
        <audio className="w-full mb-4" controls autoPlay src={audioUrl}>
          Your browser does not support audio.
        </audio>
      )}

      {loading && <p>Loading visit...</p>}
      {error && <p className="text-red-600">Error: {error}</p>}

      {visit && (
        <div className="space-y-4">
          <div className="p-4 rounded border border-slate-200 bg-white">
            <h1 className="text-2xl font-semibold">{visit.title}</h1>
            <p className="text-sm text-slate-600 mt-1">{visit.date}</p>
            <p className="text-sm text-slate-800 mt-3">{visit.summary}</p>
          </div>

          <Section title="Subjective" text={visit.subjective} />
          <Section title="Objective" text={visit.objective} />
          <Section title="Assessment" text={visit.assessment} />
          <Section title="Plan" text={visit.plan} />

          <p className="text-xs text-slate-500 pt-2">
            Demo note only. Not for clinical use.
          </p>
        </div>
      )}
    </PageContainer>
  );
};

function Section({ title, text }: { title: string; text: string }) {
  return (
    <div className="p-4 rounded border border-slate-200 bg-white">
      <h2 className="text-sm font-semibold text-slate-700 mb-2">{title}</h2>
      <p className="text-sm text-slate-900 whitespace-pre-wrap">
        {text || "—"}
      </p>
    </div>
  );
}

export default VisitDetailPage;

