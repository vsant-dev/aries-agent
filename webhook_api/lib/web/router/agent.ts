import { response, Router } from 'express';
import { dataReceivedHandler } from '../controllers/agent';

const router = Router();

router.post("/agent/webhooks/topic/connections", (req, res) => {
    res.send();
});
router.post("/agent/webhooks/topic/data-received", dataReceivedHandler);

export default router;