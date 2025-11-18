# Agent Directives for GitBook Worker Engineers and Architects

1. **Semantic Versioning**: Add a semantic version to every development document, YAML file, etc.
2. **Best Practices**: Follow established best practices for code quality and maintainability.
3. **Sprint Documentation**: Create sprints and reports for work-in-progress commits in the corresponding sprint documentation folder.  
   Example: `.github/gitbook_worker/docs/sprints/foo-sprint/bar-sprint-01.md` → `.github/gitbook_worker/docs/sprints/foo-sprint/bar-sprint-01-report-00.md`
4. **Problem-Solving Strategy**: If you get stuck, take a break. Step back a few steps and shift your perspective to gain a smarter view, then fulfill your task.
5. **Comprehensive Logging**: Write extensive logs (info, warning, error) to ensure traceability and debugging capability.
6. **Documentation Location**: Place all development documents in the `.github/gitbook_worker/docs` folder for centralized documentation.
7. **Change Tracking**: Include a change date, change history, and YAML front matter in every development document.
8. **Version Control**: Track document evolution through semantic versioning in the front matter (e.g., `version: 1.0.0`). 