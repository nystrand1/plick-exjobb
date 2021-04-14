import * as React from 'react'
import s from './Sidebar.module.scss'
import { Link, useLocation } from 'react-router-dom'
import PlickLogo from '~static/images/plick-logo.png'
import { ReactComponent as DashboardIconLight } from '~static/svg/dashboard_light.svg'
import { ReactComponent as DashboardIconDark } from '~static/svg/dashboard_dark.svg'
import { ReactComponent as DocsLinkLight } from '~static/svg/docs_light.svg'
import { ReactComponent as DocsLinkDark } from '~static/svg/docs_dark.svg'

interface ISidebarLink {
  to: string
  name: string
  active_icon: React.FunctionComponent
  passive_icon: React.FunctionComponent
}

export const Sidebar = (props) => {
  const links: ISidebarLink[] = [
    {
      to: '/',
      name: 'Dashboard',
      active_icon: DashboardIconDark,
      passive_icon: DashboardIconLight,
    },
    {
      to: '/test',
      name: 'Test',
      active_icon: DocsLinkLight,
      passive_icon: DocsLinkDark,
    },
  ]

  const renderLinks = (link: ISidebarLink, active: boolean) => {
    return (
      <Link
        to={link.to}
        key={link.to}
        className={`${s.sidebarLink} ${active ? s.active : ''}`}
      >
        {active ? <link.active_icon /> : <link.passive_icon />}
        <div className={s.linkName}>{link.name}</div>
      </Link>
    )
  }

  const path = useLocation().pathname
  return (
    <div className={s.sidebarWrapper}>
      <img src={PlickLogo} alt="plick-logo" className={s.logo} />
      <div className={s.linksWrapper}>
        {links.map((link) => renderLinks(link, path === link.to))}
      </div>
    </div>
  )
}
