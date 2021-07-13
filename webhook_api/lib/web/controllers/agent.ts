import { IpfsService } from '../services/ipfs';

const ipfsService = new IpfsService()

export const dataReceivedHandler = async (req: any, res: any): Promise<any> => {
    const body = req.body;

    const data = body.data;
    const resp = await ipfsService.store(data);
    res.send(resp);
}