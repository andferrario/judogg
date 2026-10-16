import { Navigate, Route, Routes, useLocation } from "react-router";
import { AthletePage } from "../features/athlete/AthletePage";
import { CoveragePage } from "../features/coverage/CoveragePage";
import { NotFoundPage } from "../features/notFound/NotFoundPage";
import { PenaltiesPage } from "../features/penalties/PenaltiesPage";
import { RepertoirePage } from "../features/repertoire/RepertoirePage";
import { TechniquePage } from "../features/technique/TechniquePage";
import { TechniquesPage } from "../features/techniques/TechniquesPage";
import { Layout } from "./Layout";
import { MetaGate } from "./meta";

export function App() {
  return (
    <MetaGate>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<RedirectToTechniques />} />
          <Route path="techniques" element={<TechniquesPage />} />
          <Route path="techniques/:code" element={<TechniquePage />} />
          <Route path="repertoire" element={<RepertoirePage />} />
          <Route path="penalties" element={<PenaltiesPage />} />
          <Route path="coverage" element={<CoveragePage />} />
          <Route path="athletes/:id" element={<AthletePage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </MetaGate>
  );
}

function RedirectToTechniques() {
  const { search } = useLocation();
  return <Navigate replace to={{ pathname: "/techniques", search }} />;
}
