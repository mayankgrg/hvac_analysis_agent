import { ProjectCard, ProjectCardData } from "./project-card";

export function PortfolioGrid({ projects, analyzed }: { projects: ProjectCardData[]; analyzed: boolean }) {
  return (
    <div className="grid grid-5">
      {projects.map((project) => (
        <ProjectCard key={project.project_id} data={project} analyzed={analyzed} />
      ))}
    </div>
  );
}
