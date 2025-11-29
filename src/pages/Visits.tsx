import MainNav from "@/components/MainNav";
import PageContainer from "@/components/PageContainer";
import VisitCard from "@/components/VisitCard";

// TODO: Replace with real data from backend
const mockVisits = [
  {
    id: 1,
    title: "Annual Physical - John Smith",
    date: "2024-01-15",
    summary: "Patient presented for annual physical examination. Vitals within normal range. Discussed medication adherence and lifestyle modifications. Labs ordered for follow-up.",
  },
  {
    id: 2,
    title: "Follow-up Consultation - Sarah Johnson",
    date: "2024-01-14",
    summary: "Follow-up visit for hypertension management. Blood pressure improved since last visit. Patient tolerating current medication well. Continue current treatment plan.",
  },
  {
    id: 3,
    title: "Urgent Care - Michael Brown",
    date: "2024-01-13",
    summary: "Patient presented with acute upper respiratory symptoms. Physical examination revealed mild throat inflammation. Prescribed symptomatic treatment and advised rest.",
  },
  {
    id: 4,
    title: "Diabetes Review - Emma Davis",
    date: "2024-01-12",
    summary: "Quarterly diabetes management review. HbA1c levels stable. Patient reports good compliance with diet and exercise regimen. Renewed prescriptions and scheduled next review.",
  },
];

const Visits = () => {
  return (
    <div className="min-h-screen bg-background">
      <MainNav />
      
      <PageContainer>
        <div className="space-y-6">
          <div className="space-y-2">
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
              Patient Visits
            </h1>
            <p className="text-muted-foreground">
              View and manage your clinical visit documentation
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {mockVisits.map((visit) => (
              <VisitCard
                key={visit.id}
                title={visit.title}
                date={visit.date}
                summary={visit.summary}
              />
            ))}
          </div>
        </div>
      </PageContainer>
    </div>
  );
};

export default Visits;
