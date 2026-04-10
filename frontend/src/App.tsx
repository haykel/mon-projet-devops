import KeycloakProvider, { useKeycloak } from "./components/KeycloakProvider";

function Dashboard() {
  const { username, roles, logout } = useKeycloak();

  return (
    <div>
      <h1>Hello World</h1>
      <p>Utilisateur : {username}</p>
      <p>Rôles : {roles.join(", ")}</p>
      <button onClick={logout}>Se déconnecter</button>
    </div>
  );
}

function App() {
  return (
    <KeycloakProvider>
      <Dashboard />
    </KeycloakProvider>
  );
}

export default App;
