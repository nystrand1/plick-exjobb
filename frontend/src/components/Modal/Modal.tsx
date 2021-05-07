import * as React from 'react'
import {
  Dialog,
  DialogContent,
  DialogTitle,
  Card,
  CardHeader,
  CardMedia,
  Grid,
  CardContent,
  CardActionArea,
  IconButton,
} from '@material-ui/core'
import s from './Modal.module.scss'
import { useContext } from '~contexts'
import Loading from '~static/images/loading.gif'
import { ReactComponent as ShowMore } from '~static/svg/add.svg'

export const Modal = () => {
  const { exampleAds, modalEntry, setModalEntry } = useContext()

  const handleClose = () => {
    setModalEntry(null)
  }

  const ads = exampleAds.find((ex) => ex.key === modalEntry)?.ads

  return (
    <Dialog open={!!modalEntry} onClose={handleClose} maxWidth="lg">
      <DialogTitle className={s.title}>
        {modalEntry} exempelannonser
        <IconButton aria-label="close" className={s.closeButton} onClick={handleClose}>
          <ShowMore />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers>
        <Grid container justify="center" spacing={5} direction="row">
          {ads ? (
            ads?.map((ad) => (
              <Grid key={ad.id} item>
                <Card className={s.card}>
                  <CardActionArea
                    href={ad.share_url}
                    target="_blank"
                    className={s.actionArea}
                  >
                    <CardHeader
                      title={ad.title}
                      subheader={`${ad.created_at.slice(0, 10)} ${ad.sold ? 'Såld' : ''}`}
                    />
                    <CardMedia
                      className={s.media}
                      image={ad.ad_photos[0].photo}
                      title={ad.title}
                    />
                    <CardContent>{ad.description}</CardContent>
                  </CardActionArea>
                </Card>
              </Grid>
            ))
          ) : (
            <img src={Loading} alt={'loading'} className={s.loading} />
          )}
        </Grid>
      </DialogContent>
    </Dialog>
  )
}
