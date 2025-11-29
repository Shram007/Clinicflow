import { Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";

interface VisitCardProps {
  title: string;
  date: string;
  summary: string;
}

const VisitCard = ({ title, date, summary }: VisitCardProps) => {
  return (
    <div className="bg-card border border-border rounded-xl p-6 card-shadow hover:card-hover-shadow transition-all duration-300 animate-fade-in">
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold text-card-foreground">{title}</h3>
        <div className="flex items-center text-sm text-muted-foreground">
          <Calendar className="h-4 w-4 mr-1" />
          {date}
        </div>
      </div>
      
      <p className="text-muted-foreground text-sm leading-relaxed mb-4">
        {summary}
      </p>

      <Button variant="outline" size="sm" className="w-full sm:w-auto">
        View Details
        {/* TODO: Implement visit details page */}
      </Button>
    </div>
  );
};

export default VisitCard;
