import { Link } from 'react-router-dom'
import { Home, Headphones, Mic, BarChart } from 'lucide-react'

function Navbar() {
  return (
    <nav style={styles.nav}>
      <div style={styles.container}>
        <Link to="/" style={styles.brand}>
          🎯 English Learning AI
        </Link>
        <div style={styles.links}>
          <Link to="/" style={styles.link}>
            <Home size={20} />
            <span>Inicio</span>
          </Link>
          <Link to="/listening" style={styles.link}>
            <Headphones size={20} />
            <span>Listening</span>
          </Link>
          <Link to="/speaking" style={styles.link}>
            <Mic size={20} />
            <span>Speaking</span>
          </Link>
          <Link to="/dashboard" style={styles.link}>
            <BarChart size={20} />
            <span>Progreso</span>
          </Link>
        </div>
      </div>
    </nav>
  )
}

const styles = {
  nav: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    padding: '1rem 0',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
  },
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 2rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  brand: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: 'white',
    textDecoration: 'none'
  },
  links: {
    display: 'flex',
    gap: '2rem'
  },
  link: {
    color: 'white',
    textDecoration: 'none',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    transition: 'opacity 0.3s'
  }
}

export default Navbar
