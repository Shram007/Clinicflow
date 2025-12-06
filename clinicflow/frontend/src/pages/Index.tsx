import { Link } from "react-router-dom";
import { Mic, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import MainNav from "@/components/MainNav";
import PageContainer from "@/components/PageContainer";
import MicRecorder from "@/components/MicRecorder";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <MainNav />
      
      <PageContainer className="py-16 md:py-24">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <div className="space-y-4 animate-fade-in">
            <h1 className="text-5xl md:text-6xl font-bold tracking-tight">
              <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
                ClinicFlow
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground font-medium">
              Turn doctor voice notes into structured clinical documentation.
            </p>
          </div>

          <div className="max-w-2xl mx-auto">
            <p className="text-base md:text-lg text-foreground/80 leading-relaxed">
              ClinicFlow streamlines clinical documentation by converting voice recordings 
              into structured, professional medical notes. Save time, reduce errors, and 
              focus more on patient care.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
            <Link to="/visits">
              <Button size="lg" className="gradient-hero border-0 text-primary-foreground min-w-[160px]">
                <FileText className="mr-2 h-5 w-5" />
                View Visits
              </Button>
            </Link>
            
            <MicRecorder />
          </div>

          <div className="grid md:grid-cols-3 gap-6 pt-12">
            <div className="p-6 rounded-xl bg-card border border-border card-shadow">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 mx-auto">
                <Mic className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-semibold mb-2">Voice to Text</h3>
              <p className="text-sm text-muted-foreground">
                Record clinical observations naturally with your voice
              </p>
            </div>

            <div className="p-6 rounded-xl bg-card border border-border card-shadow">
              <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center mb-4 mx-auto">
                <FileText className="h-6 w-6 text-accent" />
              </div>
              <h3 className="font-semibold mb-2">Structured Notes</h3>
              <p className="text-sm text-muted-foreground">
                Automatically formatted clinical documentation
              </p>
            </div>

            <div className="p-6 rounded-xl bg-card border border-border card-shadow">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 mx-auto">
                <svg className="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="font-semibold mb-2">Save Time</h3>
              <p className="text-sm text-muted-foreground">
                Reduce documentation time by up to 70%
              </p>
            </div>
          </div>
        </div>
      </PageContainer>
    </div>
  );
};

export default Index;
